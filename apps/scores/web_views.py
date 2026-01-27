from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.tournaments.models import Match
from .models import Score, Dispute, Evidence
from .services import ScoreService, DisputeService


@login_required
def score_submit(request, match_id):
    match = get_object_or_404(Match, pk=match_id)

    if request.method == 'POST':
        try:
            set_scores = []
            for i in range(1, 6):
                p1_score = request.POST.get(f'set{i}_player1')
                p2_score = request.POST.get(f'set{i}_player2')
                if p1_score and p2_score:
                    set_scores.append({
                        'player1': int(p1_score),
                        'player2': int(p2_score)
                    })

            if not set_scores:
                raise ValueError("At least one set score is required")

            score = ScoreService.submit_score(match, request.user, set_scores)
            messages.success(request, "Score submitted successfully!")
            return redirect('match_detail', pk=match_id)
        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'scores/score_form.html', {
        'match': match,
    })


@login_required
def score_confirm(request, pk):
    score = get_object_or_404(Score, pk=pk)

    if request.method == 'POST':
        try:
            ScoreService.confirm_score(score, request.user)
            messages.success(request, "Score confirmed!")
        except Exception as e:
            messages.error(request, str(e))

    return redirect('match_detail', pk=score.match.id)


@login_required
def dispute_list(request):
    user = request.user
    if user.role == 'ORGANIZER':
        disputes = Dispute.objects.all()
    elif user.role == 'REFEREE':
        disputes = Dispute.objects.filter(match__referee=user)
    else:
        disputes = Dispute.objects.filter(raised_by=user)

    status = request.GET.get('status')
    if status:
        disputes = disputes.filter(status=status)

    return render(request, 'scores/dispute_list.html', {
        'disputes': disputes
    })


def dispute_detail(request, pk):
    dispute = get_object_or_404(Dispute, pk=pk)
    evidence = Evidence.objects.filter(dispute=dispute)

    return render(request, 'scores/dispute_detail.html', {
        'dispute': dispute,
        'evidence': evidence,
    })


@login_required
def dispute_create(request, match_id):
    match = get_object_or_404(Match, pk=match_id)

    if request.method == 'POST':
        try:
            reason = request.POST.get('reason')
            dispute = DisputeService.create_dispute(match, request.user, reason)
            messages.success(request, "Dispute created!")
            return redirect('dispute_detail', pk=dispute.id)
        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'scores/dispute_form.html', {
        'match': match,
    })


@login_required
def dispute_resolve(request, pk):
    dispute = get_object_or_404(Dispute, pk=pk)

    if request.method == 'POST':
        try:
            resolution_notes = request.POST.get('resolution_notes')
            final_score_id = request.POST.get('final_score_id')
            final_score = Score.objects.get(pk=final_score_id) if final_score_id else None

            DisputeService.resolve_dispute(dispute, request.user, resolution_notes, final_score)
            messages.success(request, "Dispute resolved!")
            return redirect('dispute_detail', pk=pk)
        except Exception as e:
            messages.error(request, str(e))

    scores = Score.objects.filter(match=dispute.match)
    return render(request, 'scores/dispute_resolve.html', {
        'dispute': dispute,
        'scores': scores,
    })


@login_required
def evidence_add(request, dispute_id):
    dispute = get_object_or_404(Dispute, pk=dispute_id)

    if request.method == 'POST':
        try:
            description = request.POST.get('description')
            file = request.FILES.get('file')

            DisputeService.add_evidence(dispute, request.user, file, description)
            messages.success(request, "Evidence added!")
        except Exception as e:
            messages.error(request, str(e))

    return redirect('dispute_detail', pk=dispute_id)
