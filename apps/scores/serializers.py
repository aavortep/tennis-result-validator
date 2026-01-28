from rest_framework import serializers

from apps.accounts.serializers import UserPublicSerializer
from core.utils import validate_set_scores
from .models import Score, Dispute


class ScoreSerializer(serializers.ModelSerializer):
    submitted_by = UserPublicSerializer(read_only=True)
    confirmed_by = UserPublicSerializer(read_only=True)
    winner = UserPublicSerializer(read_only=True)
    match_info = serializers.SerializerMethodField()

    class Meta:
        model = Score
        fields = [
            'id', 'match', 'match_info', 'submitted_by', 'set_scores',
            'winner', 'is_confirmed', 'confirmed_by', 'confirmed_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_match_info(self, obj):
        return {
            'id': obj.match.id,
            'player1': obj.match.player1.username if obj.match.player1 else None,
            'player2': obj.match.player2.username if obj.match.player2 else None,
            'tournament': obj.match.tournament.name
        }


class ScoreSubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = ['match', 'set_scores']

    def validate_set_scores(self, value):
        is_valid, error = validate_set_scores(value)
        if not is_valid:
            raise serializers.ValidationError(error)
        return value


class ScoreUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = ['set_scores']

    def validate_set_scores(self, value):
        is_valid, error = validate_set_scores(value)
        if not is_valid:
            raise serializers.ValidationError(error)
        return value


class ScoreListSerializer(serializers.ModelSerializer):
    submitted_by_name = serializers.CharField(source='submitted_by.username', read_only=True)

    class Meta:
        model = Score
        fields = [
            'id', 'match', 'submitted_by_name', 'set_scores',
            'is_confirmed', 'created_at'
        ]


class DisputeSerializer(serializers.ModelSerializer):
    """Serializer for dispute details"""

    raised_by = UserPublicSerializer(read_only=True)
    resolved_by = UserPublicSerializer(read_only=True)
    evidence_count = serializers.SerializerMethodField()

    class Meta:
        model = Dispute
        fields = [
            'id', 'match', 'raised_by', 'reason', 'status',
            'resolved_by', 'resolution_notes', 'resolved_at',
            'evidence_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_evidence_count(self, obj):
        return obj.evidence.count()


class DisputeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispute
        fields = ['match', 'reason']


class DisputeResolveSerializer(serializers.Serializer):
    resolution_notes = serializers.CharField(required=True)
    final_score_id = serializers.IntegerField(required=False, allow_null=True)
    winner_id = serializers.IntegerField(required=False, allow_null=True)
