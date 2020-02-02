# -*- coding: utf-8 -*-
"""
Database models for course_access_groups.
"""

from __future__ import absolute_import, unicode_literals

from django.contrib.auth import get_user_model
from django.db import models
from model_utils import models as utils_models
from organizations.models import Organization
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview


class Group(utils_models.TimeStampedModel):
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
    Student membership in a Group.
    """

    group = models.ForeignKey(Group)
    user = models.OneToOneField(
        get_user_model(),
        help_text='Student. A student can only be enrolled in a single Course Access Group.'
    )


class Rule(utils_models.TimeStampedModel):
    name = models.CharField(max_length=255, help_text='A description for this assignment rule.')
    domain = models.CharField(max_length=255, db_index=True)
    group = models.ForeignKey(Group)


class CourseGroup(utils_models.TimeStampedModel):
    course = models.ForeignKey(CourseOverview)
    group = models.ForeignKey(Group)

    class Meta(object):
        unique_together = ['course', 'group']
