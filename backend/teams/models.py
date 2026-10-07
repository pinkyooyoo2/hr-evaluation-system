from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=100)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='managed_team',
        limit_choices_to={'role': 'manager'},
    )
    bonus_score = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )

    def __str__(self):
        return self.name
