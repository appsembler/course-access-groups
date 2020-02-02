# -*- coding: utf-8 -*-
"""
Database models for course_access_groups.
"""

from __future__ import absolute_import, unicode_literals

from django.contrib.auth import get_user_model
from django.db import models
from model_utils import models as utils_models
from organizations.models import Organization


class CourseAccessGroup(models.Model):
    """
    Group of students to determine which courses to show to them.

    This model is organization-aware and work exclusively in multi-site environments.
    """

    name = models.CharField(max_length=32)
    description = models.CharField(
        blank=True,
        default='',
        max_length=255,
        help_text='An optional description about this group.'
    )
    organization = models.ForeignKey(Organization)


class Membership(utils_models.TimeStampedModel):
    """
    Student membership in a CourseAccessGroup.
    """

    group = models.ForeignKey(CourseAccessGroup)
    user = models.OneToOneField(
        get_user_model(),
        help_text='Student. A student can only be enrolled in a single Course Access Group.'
    )
