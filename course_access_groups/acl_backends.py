# -*- coding: utf-8 -*-
"""
Access Control backends to implement the Course Access Groups.
"""

from __future__ import absolute_import, unicode_literals

from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from organizations.models import OrganizationCourse, UserOrganizationMapping
import six
from course_access_groups.models import (
    CourseAccessGroup,
    GroupCourse,
    Membership,
)


def is_organization_staff(user, course):
    """
    Helper to check if the user is organization staff.

    :param user: User to check access against.
    :param course: The Course or CourseOverview object to check access for.

    :return: bool

    TODO: Handle single-site setups in which organization is not important
    TODO: What if a course has two orgs? data leak I guess?
    """
    if not user.is_active:
        # Checking for `user.is_active` again. Better to be safe than sorry.
        return False

    # Same as organization.api.get_course_organizations
    course_org_ids = OrganizationCourse.objects.filter(
        course_id=six.text_type(course.id),
        active=True
    ).values('organization_id')

    return UserOrganizationMapping.objects.filter(
        user=user,
        organization_id__in=course_org_ids,
        is_active=True,
        is_amc_admin=True,
    ).exists()


def is_feature_enabled():
    """
    Helper to check Site Configuration for ENABLE_COURSE_ACCESS_GROUPS.

    :return: bool
    """
    return bool(configuration_helpers.get_value('ENABLE_COURSE_ACCESS_GROUPS', default=False))


def user_has_access(user, resource, default_has_access, options):  # pylint: disable=unused-argument
    """
    The Access Control Backend to plug the Course Access Groups feature in Open edX.

    :param user: User to check access against.
    :param resource: Usually a Course or CourseOverview object to check access for.
    :param default_has_access: The platform default access check, useful as a callback.
    :param options: Extra options, nothing in particular here.
    :return: bool: whether the user is granted access or no.
    """
    if not is_feature_enabled():
        # Plugin is turned off, maintain the platform's default behaviour.
        return default_has_access

    if not default_has_access:
        # Only permit resources that both Open edX [and] CAG rules allow.
        # i.e. Course Access Groups should not leak resources that Open edX don't want to permit.
        # e.g. In case the `course.is_deleted` feature is enabled, Open edX would prevent course access regardless
        # of the permission. It's good to have the CAG module future proof in case of such changes.
        return False

    if user.is_staff or user.is_superuser:
        return default_has_access

    if is_organization_staff(user, resource):
        return default_has_access

    user_groups = CourseAccessGroup.objects.filter(
        pk__in=Membership.objects.filter(
            user=user,
        ).values('group_id'),
    )

    return GroupCourse.objects.filter(
        course=resource,
        group__in=user_groups,
    ).exists()


__all__ = ['user_has_access']
