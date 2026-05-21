from django.contrib.auth.models import User
from django.db.models import Count

from apps.cybershield_ai.models import ForumPost, ScanHistory, TrainerAttempt


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
        'recent_scans': scans.select_related('user')[:8],
        'leaderboard': _build_leaderboard(),
    }


def _build_leaderboard():
    users = User.objects.annotate(
        scans_count=Count('scans', distinct=True),
        attempts_count=Count('trainer_attempts', distinct=True),
        posts_count=Count('forum_posts', distinct=True),
        comments_count=Count('forum_comments', distinct=True),
        likes_given_count=Count('forum_likes', distinct=True),
        likes_received_count=Count('forum_posts__likes', distinct=True),
    )

    rows = []
    for user in users:
        attempts = list(user.trainer_attempts.all())
        correct = sum(1 for item in attempts if item.is_correct)
        accuracy = round((correct / len(attempts)) * 100) if attempts else 0
        score = (
            correct * 12
            + user.scans_count * 3
            + user.posts_count * 8
            + user.comments_count * 4
            + user.likes_received_count * 2
            + user.likes_given_count
        )
        rows.append({
            'user': user,
            'score': score,
            'accuracy': accuracy,
            'scans_count': user.scans_count,
            'attempts_count': user.attempts_count,
            'posts_count': user.posts_count,
            'comments_count': user.comments_count,
            'likes_received_count': user.likes_received_count,
        })

    return sorted(rows, key=lambda item: item['score'], reverse=True)[:10]
