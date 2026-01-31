from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import (
    CanResolveDispute,
    CanSubmitScore,
    IsOrganizerOrReferee,
)
from core.exceptions import (
    DisputeError,
    InvalidStateError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)

from .models import Dispute, Evidence, Score
from .serializers import (
    DisputeCreateSerializer,
    DisputeResolveSerializer,
    DisputeSerializer,
    EvidenceCreateSerializer,
    EvidenceSerializer,
    ScoreListSerializer,
    ScoreSerializer,
    ScoreSubmitSerializer,
    ScoreUpdateSerializer,
)
from .services import DisputeService, ScoreService


class ScoreSubmitView(APIView):
    permission_classes = [CanSubmitScore]

    def post(self, request):
        serializer = ScoreSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            score = ScoreService.submit_score(
                serializer.validated_data["match"].id,
                serializer.validated_data["set_scores"],
                request.user,
            )
            return Response(ScoreSerializer(score).data, status=status.HTTP_201_CREATED)
        except (
            ValidationError,
            PermissionDeniedError,
            NotFoundError,
            InvalidStateError,
        ) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ScoreDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Score.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return ScoreUpdateSerializer
        return ScoreSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            score = ScoreService.update_score(
                self.kwargs["pk"], serializer.validated_data["set_scores"], request.user
            )
            return Response(ScoreSerializer(score).data)
        except (
            ValidationError,
            PermissionDeniedError,
            NotFoundError,
            InvalidStateError,
        ) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            ScoreService.delete_score(self.kwargs["pk"], request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except (PermissionDeniedError, NotFoundError, InvalidStateError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ScoreConfirmView(APIView):
    permission_classes = [CanSubmitScore]

    def post(self, request, pk):
        try:
            score = ScoreService.confirm_score(pk, request.user)
            return Response(
                {
                    "message": "Score confirmed successfully.",
                    "score": ScoreSerializer(score).data,
                }
            )
        except (ValidationError, PermissionDeniedError, NotFoundError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MatchScoresView(generics.ListAPIView):
    serializer_class = ScoreListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ScoreService.get_match_scores(self.kwargs["match_id"])


class DisputeCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DisputeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            dispute = DisputeService.create_dispute(
                serializer.validated_data["match"].id,
                serializer.validated_data["reason"],
                request.user,
            )
            return Response(
                DisputeSerializer(dispute).data, status=status.HTTP_201_CREATED
            )
        except (
            ValidationError,
            PermissionDeniedError,
            NotFoundError,
            DisputeError,
        ) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DisputeListView(generics.ListAPIView):
    serializer_class = DisputeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Dispute.objects.all()

        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if user.is_player:
            from django.db.models import Q

            queryset = queryset.filter(Q(match__player1=user) | Q(match__player2=user))

        elif user.is_referee:
            queryset = queryset.filter(match__referee=user)

        return queryset


class DisputeDetailView(generics.RetrieveAPIView):
    queryset = Dispute.objects.all()
    serializer_class = DisputeSerializer
    permission_classes = [IsAuthenticated]


class DisputeResolveView(APIView):
    permission_classes = [CanResolveDispute]

    def post(self, request, pk):
        serializer = DisputeResolveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            dispute = DisputeService.resolve_dispute(
                pk,
                serializer.validated_data["resolution_notes"],
                request.user,
                serializer.validated_data.get("final_score_id"),
                serializer.validated_data.get("winner_id"),
            )
            return Response(
                {
                    "message": "Dispute resolved successfully.",
                    "dispute": DisputeSerializer(dispute).data,
                }
            )
        except (
            ValidationError,
            PermissionDeniedError,
            NotFoundError,
            InvalidStateError,
        ) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DisputeReviewView(APIView):
    permission_classes = [CanResolveDispute]

    def post(self, request, pk):
        try:
            dispute = DisputeService.mark_under_review(pk, request.user)
            return Response(
                {
                    "message": "Dispute marked as under review.",
                    "dispute": DisputeSerializer(dispute).data,
                }
            )
        except (PermissionDeniedError, NotFoundError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class EvidenceCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = EvidenceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            evidence = DisputeService.add_evidence(
                serializer.validated_data["dispute"].id,
                serializer.validated_data.get("file"),
                serializer.validated_data["description"],
                request.user,
            )
            return Response(
                EvidenceSerializer(evidence).data, status=status.HTTP_201_CREATED
            )
        except (
            ValidationError,
            PermissionDeniedError,
            NotFoundError,
            InvalidStateError,
        ) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DisputeEvidenceView(generics.ListAPIView):
    serializer_class = EvidenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DisputeService.get_dispute_evidence(self.kwargs["pk"])


class OpenDisputesView(generics.ListAPIView):
    serializer_class = DisputeSerializer
    permission_classes = [IsOrganizerOrReferee]

    def get_queryset(self):
        return DisputeService.get_open_disputes()
