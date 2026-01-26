from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.tournaments.models import Match
from .models import Score
from .services import ScoreService

@login_required
def score_submit(request, match_id):
    """Submit score for a match"""

    match = get_object_or_404(Match, pk=match_id)

    if request.method == 'POST':
        try:
            # Parse set scores from form
            set_scores = []
            for i in range(1, 6):  # Up to 5 sets
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
    """Confirm a submitted score."""
    score = get_object_or_404(Score, pk=pk)

    if request.method == 'POST':
        try:
            messages.success(request, "Score confirmed!")
        except Exception as e:
            messages.error(request, str(e))

    return redirect('match_detail', pk=score.match.id)
