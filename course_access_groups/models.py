# -*- coding: utf-8 -*-
"""
Database models for course_access_groups.
"""

from __future__ import absolute_import, unicode_literals

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.utils.translation import ugettext as _
from model_utils import models as utils_models
from organizations.models import Organization
from six import text_type


class CourseAccessGroup(models.Model):
    """
    Group of students to determine which courses to show to them.

    This model is organization-aware but can also work on single-site Open edX installations.
    """

    MAX_SLUGIFY_ATTEMPTS = 100  # Ensures the `get_unique_slug` won't run forever.

    name = models.CharField(max_length=32)
    description = models.CharField(
        blank=True,
        default='',
        max_length=255,
        help_text='An optional description about this group.'
    )
    slug = models.SlugField(unique=True)
    organization = models.ForeignKey(Organization, null=True)

    @classmethod
    def generate_unique_slug(cls, org_name, group_name):
        """
        Generate a unique slug in the format of organization-group_name-87 from a group (CAG) information.

        :param org_name: The name of the organization which the CourseAccessGroup belongs to .
        :param group_name: The course access name.

        :return: string.
        """
        number_suffix = 0
        while True:
            slug_parts = []
            if org_name:
                slug_parts.append('{name}-'.format(name=org_name))
            slug_parts.append(group_name)
            if number_suffix:
                slug_parts.append(text_type(number_suffix))

            pre_slug = ' '.join(slug_parts)  # Something like `Org Group Name 64`
            slug = slugify(pre_slug, allow_unicode=False)  # Would become `org-group-name-64`
            exists = cls.objects.filter(slug=slug).exists()
            if not exists:
                return slug
            number_suffix += 1

            if number_suffix > cls.MAX_SLUGIFY_ATTEMPTS:
                raise ValidationError(
                    _('Unable to generate a unique slug for course access group: {name}').format(name=group_name)
                )

    @classmethod
    def create_with_slug(cls, **kwargs):
        """
        Create a group with a unique slug.

        :param kwargs: Same kwargs as CourseAccessGroup.__init__()
        :return: CourseAccessGroup.
        """
        group = cls(**kwargs)
        if not group.slug:
            group.slug = cls.generate_unique_slug(
                group_name=group.name,
                org_name=group.organization.short_name if group.organization else None,
            )
        group.save()
        return group


class Membership(utils_models.TimeStampedModel):
    """
    Student membership in a CourseAccessGroup.
    """

    group = models.ForeignKey(CourseAccessGroup)
    user = models.ForeignKey(
        get_user_model(),
        unique=True,  # A student can only be enrolled in a single Course Access Group.
        help_text='Student.'
    )

    @classmethod
    def clear_enrollments(cls, user):
        """
        Delete a membership.

        :param user: Learner to delete memberships for.
        :return:
        """
        cls.objects.filter(user=user).delete()
