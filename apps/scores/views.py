from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import (
    CanSubmitScore, IsOrganizerOrReferee
)
from core.exceptions import (
    ValidationError, PermissionDeniedError, NotFoundError, InvalidStateError
)
from .models import Score, Dispute
from .serializers import (
    ScoreSerializer, ScoreSubmitSerializer, ScoreUpdateSerializer,
    ScoreListSerializer, DisputeSerializer
)
from .services import ScoreService, DisputeService


class ScoreSubmitView(APIView):
    permission_classes = [CanSubmitScore]

    def post(self, request):
        serializer = ScoreSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            score = ScoreService.submit_score(
                serializer.validated_data['match'].id,
                serializer.validated_data['set_scores'],
                request.user
            )
            return Response(
                ScoreSerializer(score).data,
                status=status.HTTP_201_CREATED
            )
        except (ValidationError, PermissionDeniedError, NotFoundError, InvalidStateError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ScoreDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a score"""

    queryset = Score.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return ScoreUpdateSerializer
        return ScoreSerializer

    def update(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            score = ScoreService.update_score(
                self.kwargs['pk'],
                serializer.validated_data['set_scores'],
                request.user
            )
            return Response(ScoreSerializer(score).data)
        except (ValidationError, PermissionDeniedError, NotFoundError, InvalidStateError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request):
        try:
            ScoreService.delete_score(self.kwargs['pk'], request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except (PermissionDeniedError, NotFoundError, InvalidStateError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ScoreConfirmView(APIView):
    """Confirm an opponent's score"""

    permission_classes = [CanSubmitScore]

    def post(self, request, pk):
        try:
            score = ScoreService.confirm_score(pk, request.user)
            return Response({
                'message': 'Score confirmed successfully.',
                'score': ScoreSerializer(score).data
            })
        except (ValidationError, PermissionDeniedError, NotFoundError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MatchScoresView(generics.ListAPIView):
    """List scores for a match"""

    serializer_class = ScoreListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ScoreService.get_match_scores(self.kwargs['match_id'])


class DisputeListView(generics.ListAPIView):
    serializer_class = DisputeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Dispute.objects.all()

        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Players see only their disputes
        if user.is_player:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(match__player1=user) | Q(match__player2=user)
            )

        # Referees see disputes for their matches
        elif user.is_referee:
            queryset = queryset.filter(match__referee=user)

        return queryset


class OpenDisputesView(generics.ListAPIView):
    """List all open disputes (for organizers/referees)"""

    serializer_class = DisputeSerializer
    permission_classes = [IsOrganizerOrReferee]

    def get_queryset(self):
        return DisputeService.get_open_disputes()
