from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.accounts.permissions import (
    CanSubmitScore
)
from core.exceptions import (
    ValidationError, PermissionDeniedError, NotFoundError, InvalidStateError
)
from .serializers import (
    ScoreSerializer, ScoreSubmitSerializer
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
