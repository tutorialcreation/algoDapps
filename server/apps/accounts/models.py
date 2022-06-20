from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):
    STAFF = 1
    TRAINEE = 2
    PUBLIC = 3
    ROLE_CHOICES = (
        (STAFF, 'Staff'),
        (TRAINEE, 'Trainee'),
        (PUBLIC, 'Public'),
    )
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, null=True, blank=True)
    REQUIRED_FIELDS = ["email", "role"]
