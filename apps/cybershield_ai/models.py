from django.conf import settings
from django.db import models


class ScanHistory(models.Model):
    SCAN_TYPES = (
        ('url', 'URL Checker'),
        ('text', 'Text Analyzer'),
        ('media', 'File Scanner'),
    )

    scan_type = models.CharField(max_length=20, choices=SCAN_TYPES)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scans',
    )
    target = models.TextField()
    verdict = models.CharField(max_length=120)
    risk_score = models.PositiveSmallIntegerField(default=0)
    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_scan_type_display()}: {self.verdict} ({self.risk_score})'


class TrainerAttempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trainer_attempts',
    )
    scenario_title = models.CharField(max_length=160)
    scenario_text = models.TextField()
    correct_answer = models.BooleanField()
    user_answer = models.BooleanField()
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_correct(self):
        return self.correct_answer == self.user_answer


class ForumPost(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_posts')
    title = models.CharField(max_length=180)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ForumLike',
        related_name='liked_forum_posts',
        blank=True,
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ForumComment(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_comments')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author}: {self.body[:40]}'


class ForumLike(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')
