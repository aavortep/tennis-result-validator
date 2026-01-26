from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import (
    CanSubmitScore
)
from core.exceptions import (
    ValidationError, PermissionDeniedError, NotFoundError, InvalidStateError
)
from .models import Score
from .serializers import (
    ScoreSerializer, ScoreSubmitSerializer, ScoreUpdateSerializer
)
from .services import ScoreService


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

    def update(self, request, *args, **kwargs):
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

    def destroy(self, request, *args, **kwargs):
        try:
            ScoreService.delete_score(self.kwargs['pk'], request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except (PermissionDeniedError, NotFoundError, InvalidStateError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
