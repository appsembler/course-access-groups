"""
Mocks for the `student.models` module so tests can run.
"""
from django.contrib.auth import get_user_model
from django.db import models


class UserProfile(models.Model):
    """
    The production model is student.models.UserProfile.
    """
    user = models.OneToOneField(get_user_model(), unique=True, db_index=True, related_name='profile')
    name = models.CharField(blank=True, max_length=255, db_index=True)
