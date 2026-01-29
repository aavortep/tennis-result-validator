"""
Template-based views for tournaments.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from apps.accounts.models import User
from .models import Tournament, Match
from .services import TournamentService, MatchService
from apps.scores.models import Score, Dispute


def tournament_list(request):
    """List all tournaments."""
    tournaments = Tournament.objects.all()
    status = request.GET.get('status')
    if status:
        tournaments = tournaments.filter(status=status)

    return render(request, 'tournaments/tournament_list.html', {
        'tournaments': tournaments
    })


def tournament_detail(request, pk):
    """Tournament detail page."""
    tournament = get_object_or_404(Tournament, pk=pk)
    matches = tournament.matches.all()

    # Get available players not in tournament
    available_players = User.objects.filter(
        role=User.Role.PLAYER
    ).exclude(id__in=tournament.players.values_list('id', flat=True))

    # Get available referees not in tournament
    available_referees = User.objects.filter(
        role=User.Role.REFEREE
    ).exclude(id__in=tournament.referees.values_list('id', flat=True))

    # Handle status updates
    if request.method == 'POST' and request.user.is_authenticated:
        action = request.POST.get('action')
        try:
            if action == 'open_registration':
                TournamentService.open_registration(tournament, request.user)
                messages.success(request, "Registration is now open!")
            elif action == 'start':
                TournamentService.start_tournament(tournament, request.user)
                messages.success(request, "Tournament started!")
            elif action == 'complete':
                TournamentService.complete_tournament(tournament, request.user)
                messages.success(request, "Tournament completed!")
        except Exception as e:
            messages.error(request, str(e))
        return redirect('tournament_detail', pk=pk)

    return render(request, 'tournaments/tournament_detail.html', {
        'tournament': tournament,
        'matches': matches,
        'available_players': available_players,
        'available_referees': available_referees,
    })


@login_required
def tournament_create(request):
    """Create a new tournament."""
    if request.user.role != 'ORGANIZER':
        messages.error(request, "Only organizers can create tournaments.")
        return redirect('tournament_list')

    if request.method == 'POST':
        try:
            data = {
                'name': request.POST.get('name'),
                'description': request.POST.get('description', ''),
                'start_date': request.POST.get('start_date'),
                'end_date': request.POST.get('end_date'),
                'location': request.POST.get('location'),
                'max_players': int(request.POST.get('max_players', 32)),
            }
            tournament = TournamentService.create_tournament(data, request.user)
            messages.success(request, "Tournament created successfully!")
            return redirect('tournament_detail', pk=tournament.id)
        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'tournaments/tournament_form.html', {'tournament': None})


@login_required
def tournament_edit(request, pk):
    """Edit a tournament."""
    tournament = get_object_or_404(Tournament, pk=pk)

    if request.user != tournament.created_by:
        messages.error(request, "You can only edit your own tournaments.")
        return redirect('tournament_detail', pk=pk)

    if request.method == 'POST':
        try:
            data = {
                'name': request.POST.get('name'),
                'description': request.POST.get('description', ''),
                'start_date': request.POST.get('start_date'),
                'end_date': request.POST.get('end_date'),
                'location': request.POST.get('location'),
                'max_players': int(request.POST.get('max_players', 32)),
            }
            TournamentService.update_tournament(tournament, data, request.user)
            messages.success(request, "Tournament updated!")
            return redirect('tournament_detail', pk=pk)
        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'tournaments/tournament_form.html', {'tournament': tournament})


@login_required
def tournament_add_player(request, pk):
    """Add player to tournament."""
    tournament = get_object_or_404(Tournament, pk=pk)

    if request.method == 'POST':
        player_id = request.POST.get('player_id')
        try:
            TournamentService.add_player(tournament, int(player_id), request.user)
            messages.success(request, "Player added!")
        except Exception as e:
            messages.error(request, str(e))

    return redirect('tournament_detail', pk=pk)


@login_required
def tournament_remove_player(request, pk, player_id):
    """Remove player from tournament."""
    tournament = get_object_or_404(Tournament, pk=pk)

    if request.method == 'POST':
        try:
            TournamentService.remove_player(tournament, player_id, request.user)
            messages.success(request, "Player removed!")
        except Exception as e:
            messages.error(request, str(e))

    return redirect('tournament_detail', pk=pk)


@login_required
def tournament_add_referee(request, pk):
    """Add referee to tournament."""
    tournament = get_object_or_404(Tournament, pk=pk)

    if request.method == 'POST':
        referee_id = request.POST.get('referee_id')
        try:
            TournamentService.add_referee(tournament, int(referee_id), request.user)
            messages.success(request, "Referee added!")
        except Exception as e:
            messages.error(request, str(e))

    return redirect('tournament_detail', pk=pk)


@login_required
def my_matches(request):
    """List user's matches."""
    user = request.user
    if user.role == 'REFEREE':
        matches = Match.objects.filter(referee=user)
    elif user.role == 'PLAYER':
        matches = Match.objects.filter(Q(player1=user) | Q(player2=user))
    else:
        matches = Match.objects.none()

    return render(request, 'tournaments/match_list.html', {'matches': matches})


def match_detail(request, pk):
    """Match detail page."""
    match = get_object_or_404(Match, pk=pk)
    scores = Score.objects.filter(match=match)
    disputes = Dispute.objects.filter(match=match)

    # Handle match start
    if request.method == 'POST' and request.user.is_authenticated:
        action = request.POST.get('action')
        if action == 'start':
            try:
                MatchService.start_match(match, request.user)
                messages.success(request, "Match started!")
            except Exception as e:
                messages.error(request, str(e))
        return redirect('match_detail', pk=pk)

    return render(request, 'tournaments/match_detail.html', {
        'match': match,
        'scores': scores,
        'disputes': disputes,
    })


@login_required
def match_create(request, tournament_id):
    """Create a new match."""
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    if request.method == 'POST':
        try:
            data = {
                'tournament': tournament,
                'player1': User.objects.get(id=request.POST.get('player1')) if request.POST.get('player1') else None,
                'player2': User.objects.get(id=request.POST.get('player2')) if request.POST.get('player2') else None,
                'referee': User.objects.get(id=request.POST.get('referee')) if request.POST.get('referee') else None,
                'round': request.POST.get('round', 'R32'),
                'court': request.POST.get('court', ''),
            }
            match = MatchService.create_match(data, request.user)
            messages.success(request, "Match created!")
            return redirect('tournament_detail', pk=tournament_id)
        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'tournaments/match_form.html', {
        'tournament': tournament,
        'players': tournament.players.all(),
        'referees': tournament.referees.all(),
    })


@login_required
def match_edit(request, pk):
    """Edit a match."""
    match = get_object_or_404(Match, pk=pk)

    if request.method == 'POST':
        match.court = request.POST.get('court', '')
        match.round = request.POST.get('round', match.round)
        scheduled = request.POST.get('scheduled_time')
        if scheduled:
            match.scheduled_time = scheduled
        match.save()
        messages.success(request, "Match updated!")
        return redirect('match_detail', pk=pk)

    return render(request, 'tournaments/match_form.html', {
        'match': match,
        'tournament': match.tournament,
        'players': match.tournament.players.all(),
        'referees': match.tournament.referees.all(),
    })
