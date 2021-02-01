"""
Provides fake models for openedx.core.djangoapps.content.course_overviews

Overview
--------

The purpose of this module is to provide the minimum models in order to mock
Course Access Group interaction with the edx-platform models.
"""


from django.db import models
from opaque_keys.edx.django.models import CourseKeyField


class CourseOverview(models.Model):
    """
    Minimal mock model for the edx-platform 'CourseOverview' model.
    """
    id = CourseKeyField(db_index=True, primary_key=True, max_length=255)
    display_name = models.TextField(null=True)
    org = models.TextField(max_length=255)
    number = models.TextField()

    @property
    def display_name_with_default(self):
        return self.display_name

    @property
    def display_number_with_default(self):
        return self.number

    @property
    def display_org_with_default(self):
        return self.org

    def __str__(self):
        return str(self.id)  # noqa: F821
