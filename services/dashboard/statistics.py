from apps.cybershield_ai.models import ScanHistory, TrainerAttempt


def build_dashboard():
    scans = ScanHistory.objects.all()
    attempts = TrainerAttempt.objects.all()
    total_attempts = attempts.count()
    correct_attempts = sum(1 for item in attempts if item.is_correct)

    return {
        'total_scans': scans.count(),
        'high_risk_scans': scans.filter(risk_score__gte=70).count(),
        'trainer_attempts': total_attempts,
        'trainer_accuracy': round((correct_attempts / total_attempts) * 100) if total_attempts else 0,
        'recent_scans': scans[:8],
    }
