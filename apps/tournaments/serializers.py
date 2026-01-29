"""
Serializers for tournaments.
"""

from rest_framework import serializers

from apps.accounts.serializers import UserPublicSerializer
from .models import Tournament, Match


class TournamentSerializer(serializers.ModelSerializer):
    """Serializer for tournament details."""

    created_by = UserPublicSerializer(read_only=True)
    player_count = serializers.ReadOnlyField()

    class Meta:
        model = Tournament
        fields = [
            'id', 'name', 'description', 'start_date', 'end_date',
            'location', 'status', 'max_players', 'player_count',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']


class TournamentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tournaments."""

    class Meta:
        model = Tournament
        fields = [
            'name', 'description', 'start_date', 'end_date',
            'location', 'max_players'
        ]

    def validate(self, attrs):
        if attrs['start_date'] > attrs['end_date']:
            raise serializers.ValidationError({
                'end_date': 'End date must be after start date.'
            })
        return attrs


class TournamentListSerializer(serializers.ModelSerializer):
    """Serializer for tournament list."""

    player_count = serializers.ReadOnlyField()

    class Meta:
        model = Tournament
        fields = [
            'id', 'name', 'start_date', 'end_date',
            'location', 'status', 'player_count', 'max_players'
        ]


class TournamentDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for tournament with players and referees."""

    created_by = UserPublicSerializer(read_only=True)
    players = UserPublicSerializer(many=True, read_only=True)
    referees = UserPublicSerializer(many=True, read_only=True)
    player_count = serializers.ReadOnlyField()

    class Meta:
        model = Tournament
        fields = [
            'id', 'name', 'description', 'start_date', 'end_date',
            'location', 'status', 'max_players', 'player_count',
            'created_by', 'players', 'referees', 'created_at', 'updated_at'
        ]


class MatchSerializer(serializers.ModelSerializer):
    """Serializer for match details."""

    player1 = UserPublicSerializer(read_only=True)
    player2 = UserPublicSerializer(read_only=True)
    referee = UserPublicSerializer(read_only=True)
    winner = UserPublicSerializer(read_only=True)
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)

    class Meta:
        model = Match
        fields = [
            'id', 'tournament', 'tournament_name', 'player1', 'player2',
            'referee', 'scheduled_time', 'court', 'round', 'status',
            'winner', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MatchCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating matches."""

    class Meta:
        model = Match
        fields = [
            'tournament', 'player1', 'player2', 'referee',
            'scheduled_time', 'court', 'round'
        ]


class MatchListSerializer(serializers.ModelSerializer):
    """Serializer for match list."""

    player1_name = serializers.CharField(source='player1.username', read_only=True)
    player2_name = serializers.CharField(source='player2.username', read_only=True)
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)

    class Meta:
        model = Match
        fields = [
            'id', 'tournament_name', 'player1_name', 'player2_name',
            'scheduled_time', 'court', 'round', 'status'
        ]


class AddPlayerSerializer(serializers.Serializer):
    """Serializer for adding player to tournament."""

    player_id = serializers.IntegerField()


class AssignRefereeSerializer(serializers.Serializer):
    """Serializer for assigning referee to match."""

    referee_id = serializers.IntegerField()


class AssignPlayersSerializer(serializers.Serializer):
    """Serializer for assigning players to match."""

    player1_id = serializers.IntegerField()
    player2_id = serializers.IntegerField()

    def validate(self, attrs):
        if attrs['player1_id'] == attrs['player2_id']:
            raise serializers.ValidationError('Players must be different.')
        return attrs
