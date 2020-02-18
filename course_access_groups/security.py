# -*- coding: utf-8 -*-
"""
Course Access Groups permission and authentication classes.
"""

from __future__ import absolute_import, unicode_literals

from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
    TokenAuthentication,
)
from organizations.models import Organization, UserOrganizationMapping
from rest_framework.permissions import IsAuthenticated, BasePermission
from django.contrib.sites import shortcuts as sites_shortcuts


def is_active_staff_or_superuser(user):
    """
    Checks if user is active or superuser.
    """
    return user and user.is_active and (
        user.is_staff or user.is_superuser
    )


def is_site_admin_user(request):
    """
    Determines if the requesting user has access to site admin data

    * If Figures is running in standalone mode, then the user needs to be staff
      or superuser.
    * If figures is running in multisite mode, then the user needs to belong to
      an organizations mapped to the specified site and have `is_amc_admin` set
      to `True`

    ## What this function does

    1. Get the current site (matching the request)
    2. Get the orgs for the site. We assume only one org
    3. Get the user org mappings for the orgs and user in the request
    4. Check the uom record if user is admin and active
    """
    if is_active_staff_or_superuser(request.user):
        return True

    if not request.user.is_active:
        return False

    current_site = sites_shortcuts.get_current_site(request)
    org_ids = Organization.objects.filter(sites__in=[current_site]).values_list('id', flat=True)
    return UserOrganizationMapping.objects.filter(
        organization_id__in=org_ids,
        user=request.user,
        is_active=True,
        is_amc_admin=True,
    ).exists()


class IsSiteAdminUser(BasePermission):
    """
    Allow access to only site admins if in multisite mode or staff or superuser
    if in standalone mode
    """

    def has_permission(self, request, view):
        return is_site_admin_user(request)


class CommonAuthMixin(object):
    """
    Provides a common authorization base for the Figures API views.
    """
    authentication_classes = (
        BasicAuthentication,
        SessionAuthentication,
        TokenAuthentication,
    )
    permission_classes = (
        IsAuthenticated,
        # IsSiteAdminUser,
    )
