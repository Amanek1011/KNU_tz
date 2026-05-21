from django.contrib import admin

from .models import ScanHistory, TrainerAttempt


@admin.register(ScanHistory)
class ScanHistoryAdmin(admin.ModelAdmin):
    list_display = ('scan_type', 'verdict', 'risk_score', 'created_at')
    list_filter = ('scan_type', 'verdict')
    search_fields = ('target', 'explanation')


@admin.register(TrainerAttempt)
class TrainerAttemptAdmin(admin.ModelAdmin):
    list_display = ('scenario_title', 'correct_answer', 'user_answer', 'created_at')
    search_fields = ('scenario_title', 'scenario_text', 'feedback')

# Register your models here.
