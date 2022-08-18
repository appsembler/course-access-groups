# -*- coding: utf-8 -*-
"""
Course Access Groups permission and authentication classes.
"""


import logging

from django.contrib.sites.models import Site
from django.core.exceptions import MultipleObjectsReturned
from organizations.models import Organization
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from tahoe_sites.api import (
    get_current_organization,
    get_organization_by_course,
    get_organization_by_uuid,
    is_active_admin_on_organization,
)

from .models import CourseAccessGroup, GroupCourse, Membership, PublicCourse
from .openedx_modules import OAuth2Authentication

log = logging.getLogger(__name__)


def is_organization_staff(user, course):
    """
    Helper to check if the user is organization staff.

    Q: What if a course has two orgs?
    A: No problem. This function raises `MultipleObjectsReturned`

    :param user: User to check access against.
    :param course: The Course or CourseOverview object to check access for.

    :return: bool
    """
    if not user.is_active:
        # Checking for `user.is_active` again. Better to be safe than sorry.
        return False

    try:
        course_organization = get_organization_by_course(course_id=course.id)
    except Organization.DoesNotExist:
        # Safely handle the exception errors by assuming the user is not a staff.
        return False
    except MultipleObjectsReturned:
        log.warning(
            'Course Access Group: This module expects a one:one relationship between organizations and course. '
            'Raised by course (%s)', course.id
        )
        return False

    return is_active_admin_on_organization(user=user, organization=course_organization)


def get_requested_organization(request):
    """
    Return a single organization for the request based on two strategies.

        - Strategy no 1: If the `GET.site_uuid` parameter find the Organization by `site_uuid`
                         - This only works for superuser accounts.
        - Strategy no 2: Get the current organization.

    Note: In Tahoe terms `site` and `organization` is interchangeable -- same goes for
          is `site_uuid` and `organization_uuid`.

    :raise whatever exceptions get_current_organization().

    :return Organization.
    """
    organization_uuid = request.GET.get('organization_uuid')
    if organization_uuid:
        if is_active_staff_or_superuser(request.user):
            return get_organization_by_uuid(organization_uuid)
        else:
            raise PermissionDenied('Not permitted to use the `organization_uuid` parameter.')
    else:
        return get_current_organization(request)


def is_site_admin_user(request):
    """
    Determines if the requesting user has access to site admin data

    ## What this function does

    1. Get the current site (matching the request)
    2. Get the orgs for the site
    3. Get the user org mappings for the orgs and user in the request
    4. Check with tahoe_sites if user is an active admin

    # TODO: Refactor with `is_organization_staff`.
    """
    if not request.user.is_active:
        return False

    if is_active_staff_or_superuser(request.user):
        return True

    try:
        # Ensure strict one site per organization to simplify security checks.
        current_organization = get_current_organization(request)
    except (Site.DoesNotExist, Organization.DoesNotExist, Organization.MultipleObjectsReturned):
        log.exception(
            'Course Access Group: This module expects a one:one relationship between organizations and sites. '
            'This exception should not happen.'
        )
        return False

    return is_active_admin_on_organization(user=request.user, organization=current_organization)


def is_course_with_public_access(course):
    """
    Check PublicCourse access within the user's organization(s).

    :param user: User model object.
    :param course: CourseOverview model object.
    :return: bool.
    """
    return PublicCourse.objects.filter(course_id=course.id).exists()


class IsSiteAdminUser(BasePermission):
    """
    Allow access to only site admins if in multisite mode or staff or superuser
    if in standalone mode
    """

    def has_permission(self, request, view):
        return is_site_admin_user(request)


class CommonAuthMixin:
    """
    Provides a common authorization base for the Course Access Groups API views.
    """

    authentication_classes = (
        BasicAuthentication,
        SessionAuthentication,
        TokenAuthentication,
        OAuth2Authentication,
    )
    permission_classes = (
        IsAuthenticated,
        IsSiteAdminUser,
    )


def is_active_staff_or_superuser(user):
    """
    Checks if user is active staff or superuser.
    """
    return user and user.is_active and (user.is_staff or user.is_superuser)


def user_has_access_to_course(user, course):
    """
    Main function to check if user has access.

    :param user: User to check access against.
    :param course: CourseDescriptorWithMixins or CourseOverview object to check access for.
    :return: bool: whether the user is granted access or no.
    """
    if is_course_with_public_access(course=course):
        return True

    if not user.is_authenticated:
        # AnonymousUser cannot have Membership.
        return False

    if is_active_staff_or_superuser(user):
        return True

    if is_organization_staff(user, course):
        return True

    user_groups = CourseAccessGroup.objects.filter(
        pk__in=Membership.objects.filter(
            user=user,
        ).values('group_id'),
    )

    return GroupCourse.objects.filter(
        course_id=course.id,
        group__in=user_groups,
    ).exists()
