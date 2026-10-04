from django.db import models
from django.contrib.auth.models import AbstractUser


# Create custom user model
class Player(AbstractUser):
    total_matches = models.PositiveIntegerField(default=0)
    total_win = models.PositiveIntegerField(default=0)
    total_elim = models.PositiveIntegerField(default=0)
    total_deaths = models.PositiveIntegerField(default=0)
    total_tokens = models.PositiveIntegerField(default=0)
