from django.contrib import admin

from .models import Dispute, Evidence, Score


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ["match", "submitted_by", "winner", "is_confirmed", "created_at"]
    list_filter = ["is_confirmed", "created_at"]
    search_fields = ["match__tournament__name", "submitted_by__username"]
    raw_id_fields = ["match", "submitted_by", "winner", "confirmed_by"]


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ["match", "raised_by", "status", "resolved_by", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["match__tournament__name", "raised_by__username", "reason"]
    raw_id_fields = ["match", "raised_by", "resolved_by", "final_score"]


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ["dispute", "submitted_by", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["dispute__match__tournament__name", "description"]
    raw_id_fields = ["dispute", "submitted_by"]
