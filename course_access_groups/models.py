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


class CourseAccessGroup(utils_models.TimeStampedModel):
    """
    Group of learners to determine which courses to show to them.

    This model is organization-aware and work exclusively in multi-site environments.
    """

    name = models.CharField(max_length=32)
    description = models.CharField(
        blank=True,
        default='',
        max_length=255,
        help_text='An optional description about this group.'
    )
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)


class Membership(utils_models.TimeStampedModel):
    """
    Learner membership in a Group.
    """

    # A learner with no Membership has no access to any course.
    group = models.ForeignKey(CourseAccessGroup, on_delete=models.CASCADE)
    user = models.OneToOneField(
        get_user_model(),
        help_text='Learner. A learner can only be enrolled in a single Course Access Group.'
    )


class MembershipRule(utils_models.TimeStampedModel):
    """
    Email domain based rule to automatically assign learners to groups.
    """

    name = models.CharField(max_length=255, help_text='A description for this assignment rule.')
    # TODO: Add a new wild-card rule to assign learners with no rules to a specific group.
    domain = models.CharField(max_length=255, db_index=True, help_text='The learner email domain e.g. "example.com".')
    group = models.ForeignKey(CourseAccessGroup, on_delete=models.CASCADE)


class GroupCourse(utils_models.TimeStampedModel):
    """
    Many-to-many relationship to set which course belongs to which group.

    This similar to using ManyToManyField on the `CourseAccessGroup` model,
    extracting it here to make it easy to work with API ViewSets.
    """

    course = models.ForeignKey(CourseOverview, on_delete=models.CASCADE)
    group = models.ForeignKey(CourseAccessGroup, on_delete=models.CASCADE)

    class Meta(object):
        unique_together = ['course', 'group']
