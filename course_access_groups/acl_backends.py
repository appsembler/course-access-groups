"""
Access Control backends to implement the Course Access Groups.
"""

from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from organizations.api import get_course_organizations
from organizations.models import UserOrganizationMapping
from course_access_groups.models import (
    CourseAccessGroup,
    GroupCourse,
    Membership,
)


def is_organization_staff(user, course):
    """
    Helper to check if the user is organization staff.

    TODO: Handle single-site setups in which organization is not important
    """
    # TODO: What if a course has two orgs? data leak I guess?
    organizations = get_course_organizations(course.id)
    if not len(organizations):
        return False

    return UserOrganizationMapping.objects.filter(
        user=user,
        organization_id__in=[org['id'] for org in organizations],
        is_active=True,
        is_amc_admin=True,
    ).exists()


def is_feature_enabled():
    """
    Helper to check Site Configuration for ENABLE_COURSE_ACCESS_GROUPS.
    :return:
    """
    return bool(configuration_helpers.get_value('ENABLE_COURSE_ACCESS_GROUPS', default=False))


def default_backend(user, resource, default_has_access, options):  # pylint: disable=unused-argument
    """
    The Access Control Backend to plug the Course Access Groups feature in Open edX.
    """
    if not is_feature_enabled():
        # Plugin is turned off, maintain the platform's default behaviour.
        return default_has_access

    if not default_has_access:
        # Ensures this backend won't leak resources by mistake.
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


__all__ = ['default_backend']
