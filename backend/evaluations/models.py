from django.conf import settings
from django.db import models


class EvaluationItem(models.Model):
    name = models.CharField(max_length=200)
    weight = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, default='')

    def __str__(self):
        return self.name


class EvaluationResponse(models.Model):
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='responses_received',
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='responses_submitted',
    )
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='evaluations')
    is_submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)
    score_values = models.JSONField(default=dict, blank=True)
    temporary_save = models.JSONField(default=dict, blank=True)
    progress = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.employee} -> {self.manager}'
