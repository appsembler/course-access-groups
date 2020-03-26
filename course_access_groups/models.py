# -*- coding: utf-8 -*-
"""
Database models for course_access_groups.
"""

from __future__ import absolute_import, unicode_literals

from django.contrib.auth import get_user_model
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from model_utils import models as utils_models
from organizations.models import Organization, UserOrganizationMapping
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

from course_access_groups.validators import validate_domain


@python_2_unicode_compatible
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

    def __str__(self):
        return self.name


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
    automatic = models.BooleanField(
        default=False,
        help_text='If created by MembershipRule',
    )

    @classmethod
    def create_from_rules(cls, user):
        """
        Automatically enroll a user based on existing MembershipRule.

        :param user:
        :raise ValueError if the user is not active.
        :return: Membership (or None)
        """
        if not user.is_active:
            # Ensure that only users with verified emails are enrolled the group
            # This error should not happen in production.
            # If it does, look at the both the `Registration` class and the USER_ACCOUNT_ACTIVATED signal in Open edX.
            raise ValueError('Course Access Groups: Unable to create automatic Membership for inactive user.')

        _, email_domain = user.email.rsplit('@', 1)

        # Ideally an exception should be thrown if there's more than one organization
        # but such error is out of the scope of the CAG module.
        user_orgs = Organization.objects.filter(
            pk__in=UserOrganizationMapping.objects.filter(user=user, is_active=True).values('organization_id'),
        )
        rule = MembershipRule.objects.filter(
            domain=email_domain,
            group__organization=user_orgs,
        ).first()

        if rule:
            membership, _created = cls.objects.get_or_create(
                user=user,
                defaults={
                    'group': rule.group,
                    'automatic': True,
                },
            )
            return membership


class MembershipRule(utils_models.TimeStampedModel):
    """
    Email domain based rule to automatically assign learners to groups.
    """

    name = models.CharField(max_length=255, help_text='A description for this assignment rule.')
    domain = models.CharField(
        max_length=255,
        db_index=True,
        validators=[validate_domain],
        help_text='The learner email domain e.g. "example.com".',
    )
    group = models.ForeignKey(CourseAccessGroup, on_delete=models.CASCADE)


class PublicCourse(utils_models.TimeStampedModel):
    """
    Model to mark courses as public to exempt from the Course Access Group rules.
    """

    course = models.OneToOneField(CourseOverview, related_name='public_course', on_delete=models.CASCADE)


class GroupCourse(utils_models.TimeStampedModel):
    """
    Many-to-many relationship to set which course belongs to which group.

    This similar to using ManyToManyField on the `CourseAccessGroup` model,
    extracting it here to make it easy to work with API ViewSets.
    """

    course = models.ForeignKey(CourseOverview, related_name='group_courses', on_delete=models.CASCADE)
    group = models.ForeignKey(CourseAccessGroup, on_delete=models.CASCADE)

    class Meta(object):
        unique_together = ['course', 'group']
