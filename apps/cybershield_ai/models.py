from django.db import models


class ScanHistory(models.Model):
    SCAN_TYPES = (
        ('url', 'Ссылка'),
        ('text', 'Текст'),
        ('media', 'Медиа'),
    )

    scan_type = models.CharField(max_length=20, choices=SCAN_TYPES)
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
    scenario_title = models.CharField(max_length=160)
    scenario_text = models.TextField()
    correct_answer = models.BooleanField()
    user_answer = models.BooleanField()
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_correct(self):
        return self.correct_answer == self.user_answer

# Create your models here.
