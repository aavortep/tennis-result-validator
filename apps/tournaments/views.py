from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsOrganizer, IsOrganizerOrReadOnly
from core.exceptions import (
    InvalidStateError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)

from .models import Match, Tournament
from .serializers import (
    AddPlayerSerializer,
    AssignPlayersSerializer,
    AssignRefereeSerializer,
    MatchCreateSerializer,
    MatchListSerializer,
    MatchSerializer,
    TournamentCreateSerializer,
    TournamentDetailSerializer,
    TournamentListSerializer,
    TournamentSerializer,
)
from .services import MatchService, TournamentService


class TournamentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsOrganizerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TournamentCreateSerializer
        return TournamentListSerializer

    def get_queryset(self):
        queryset = Tournament.objects.all()
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

    def perform_create(self, serializer):
        try:
            tournament = TournamentService.create_tournament(
                serializer.validated_data, self.request.user
            )
            serializer.instance = tournament
        except (ValidationError, PermissionDeniedError) as e:
            raise serializers.ValidationError(str(e))


class TournamentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tournament.objects.all()
    permission_classes = [IsOrganizerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TournamentDetailSerializer
        return TournamentSerializer

    def perform_update(self, serializer):
        try:
            TournamentService.update_tournament(
                self.get_object(), serializer.validated_data, self.request.user
            )
        except (ValidationError, PermissionDeniedError, InvalidStateError) as e:
            from rest_framework import serializers

            raise serializers.ValidationError(str(e))

    def perform_destroy(self, instance):
        try:
            TournamentService.delete_tournament(instance, self.request.user)
        except (PermissionDeniedError, InvalidStateError) as e:
            from rest_framework import serializers
            raise serializers.ValidationError(str(e))


class TournamentAddPlayerView(APIView):
    permission_classes = [IsOrganizer]

    def post(self, request, pk):
        serializer = AddPlayerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            tournament = Tournament.objects.get(pk=pk)
            TournamentService.add_player(
                tournament, serializer.validated_data["player_id"], request.user
            )
            return Response({"message": "Player added successfully."})
        except Tournament.DoesNotExist:
            return Response(
                {"error": "Tournament not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except (ValidationError, NotFoundError, InvalidStateError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TournamentRemovePlayerView(APIView):
    permission_classes = [IsOrganizer]

    def delete(self, request, pk, player_id):
        try:
            tournament = Tournament.objects.get(pk=pk)
            TournamentService.remove_player(tournament, player_id, request.user)
            return Response({"message": "Player removed successfully."})
        except Tournament.DoesNotExist:
            return Response(
                {"error": "Tournament not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except (PermissionDeniedError, InvalidStateError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TournamentAddRefereeView(APIView):
    permission_classes = [IsOrganizer]

    def post(self, request, pk):
        serializer = AddPlayerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            tournament = Tournament.objects.get(pk=pk)
            TournamentService.add_referee(
                tournament, serializer.validated_data["player_id"], request.user
            )
            return Response({"message": "Referee added successfully."})
        except Tournament.DoesNotExist:
            return Response(
                {"error": "Tournament not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except (ValidationError, NotFoundError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TournamentStatusView(APIView):
    permission_classes = [IsOrganizer]

    def post(self, request, pk):
        action = request.data.get("action")

        try:
            tournament = Tournament.objects.get(pk=pk)

            if action == "open_registration":
                TournamentService.open_registration(tournament, request.user)
            elif action == "start":
                TournamentService.start_tournament(tournament, request.user)
            elif action == "complete":
                TournamentService.complete_tournament(tournament, request.user)
            else:
                return Response(
                    {"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST
                )

            return Response(
                {
                    "message": f"Tournament status updated to {tournament.status}.",
                    "status": tournament.status,
                }
            )
        except Tournament.DoesNotExist:
            return Response(
                {"error": "Tournament not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except (PermissionDeniedError, InvalidStateError, ValidationError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TournamentMatchesView(generics.ListAPIView):
    serializer_class = MatchListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Match.objects.filter(tournament_id=self.kwargs["pk"])


class MatchListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsOrganizerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return MatchCreateSerializer
        return MatchListSerializer

    def get_queryset(self):
        queryset = Match.objects.all()
        tournament_id = self.request.query_params.get("tournament")
        status_filter = self.request.query_params.get("status")

        if tournament_id:
            queryset = queryset.filter(tournament_id=tournament_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    def perform_create(self, serializer):
        try:
            match = MatchService.create_match(
                serializer.validated_data, self.request.user
            )
            serializer.instance = match
        except (ValidationError, PermissionDeniedError, InvalidStateError) as e:
            from rest_framework import serializers
            raise serializers.ValidationError(str(e))


class MatchDetailView(generics.RetrieveAPIView):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = [IsAuthenticated]


class MyMatchesView(generics.ListAPIView):
    serializer_class = MatchListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_referee:
            return Match.objects.filter(referee=user)
        elif user.is_player:
            return Match.objects.filter(Q(player1=user) | Q(player2=user))
        return Match.objects.none()


class MatchAssignPlayersView(APIView):
    permission_classes = [IsOrganizer]

    def put(self, request, pk):
        serializer = AssignPlayersSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            match = Match.objects.get(pk=pk)
            MatchService.assign_players(
                match,
                serializer.validated_data["player1_id"],
                serializer.validated_data["player2_id"],
                request.user,
            )
            return Response(MatchSerializer(match).data)
        except Match.DoesNotExist:
            return Response(
                {"error": "Match not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except (ValidationError, NotFoundError, InvalidStateError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MatchAssignRefereeView(APIView):
    permission_classes = [IsOrganizer]

    def put(self, request, pk):
        serializer = AssignRefereeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            match = Match.objects.get(pk=pk)
            MatchService.assign_referee(
                match, serializer.validated_data["referee_id"], request.user
            )
            return Response(MatchSerializer(match).data)
        except Match.DoesNotExist:
            return Response(
                {"error": "Match not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except (NotFoundError, PermissionDeniedError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MatchStartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            match = Match.objects.get(pk=pk)
            MatchService.start_match(match, request.user)
            return Response({"message": "Match started.", "status": match.status})
        except Match.DoesNotExist:
            return Response(
                {"error": "Match not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except (PermissionDeniedError, InvalidStateError, ValidationError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


from rest_framework import serializers
