# -*- coding: utf-8 -*-
"""
Test the authentication and permission of Course Access Groups.
"""

from __future__ import absolute_import, unicode_literals

import pytest
from django.contrib.auth import get_user_model
from django.contrib.sites import shortcuts as sites_shortcuts
from rest_framework.test import APIRequestFactory

from organizations.models import UserOrganizationMapping
from course_access_groups.security import (
    is_active_staff_or_superuser,
    IsSiteAdminUser,
)

from test_utils import create_standard_test_users
from test_utils.factories import (
    OrganizationFactory,
    SiteFactory,
    UserFactory,
)


@pytest.mark.django_db
class TestStaffSuperuserHelper(object):
    """
    Tests for security.is_active_staff_or_superuser.
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        create_standard_test_users()

    def test_no_user(self):
        assert not is_active_staff_or_superuser(None)

    @pytest.mark.parametrize('username, allow', [
        ('regular_user', False),
        ('staff_user', True),
        ('super_user', True),
        ('superstaff_user', True),
    ])
    def test_active_user(self, username, allow):
        user = get_user_model().objects.get(username=username)
        assert is_active_staff_or_superuser(user) == allow

    @pytest.mark.parametrize('username', [
        'regular_user',
        'staff_user',
        'super_user',
        'superstaff_user',
    ])
    def test_inactive_user(self, username):
        user = get_user_model().objects.get(username=username)
        user.is_active = False
        assert not is_active_staff_or_superuser(user)


@pytest.mark.django_db
class TestSiteAdminPermissions(object):
    """
    Test for the IsSiteAdminUser permission class.
    """

    @pytest.fixture(autouse=True)
    def setup(self, db, monkeypatch):
        self.site = SiteFactory()
        self.organization = OrganizationFactory(sites=[self.site])
        self.callers = [
            UserFactory.create(username='alpha_nonadmin'),
            UserFactory.create(username='alpha_site_admin'),
            UserFactory.create(username='nosite_staff'),
        ]
        self.user_organization_mappings = [
            UserOrganizationMapping.objects.create(
                user=self.callers[0],
                organization=self.organization),
            UserOrganizationMapping.objects.create(
                user=self.callers[1],
                organization=self.organization,
                is_amc_admin=True)
        ]
        self.callers += create_standard_test_users()
        self.request = APIRequestFactory().get('/')
        self.request.META['HTTP_HOST'] = self.site.domain
        monkeypatch.setattr(sites_shortcuts, 'get_current_site', self.get_test_site)

    def get_test_site(self, request):  # pylint: disable=unused-argument
        """
        Mock django.contrib.sites.shortcuts.get_current_site.

        :return: Site.
        """
        return self.site

    @pytest.mark.parametrize('username, allow', [
        ('regular_user', False),
        ('staff_user', True),
        ('super_user', True),
        ('superstaff_user', True),
        ('alpha_nonadmin', False),
        ('alpha_site_admin', True),
        ('nosite_staff', False),
    ])
    def test_is_site_admin_user(self, username, allow):
        """
        Ensure only site (org) admins have access.
        """
        self.request.user = get_user_model().objects.get(username=username)
        permission = IsSiteAdminUser().has_permission(self.request, None)
        assert permission == allow, 'User "{username}" should have access'.format(username=username)

        # Verify that inactive users are denied permission
        self.request.user.is_active = False
        permission = IsSiteAdminUser().has_permission(self.request, None)
        assert not permission, 'username: "{username}"'.format(username=username)

    @pytest.mark.parametrize('username, allow', [
        ('regular_user', False),
        ('staff_user', True),
        ('super_user', True),
        ('superstaff_user', True),
        ('alpha_nonadmin', False),
        ('alpha_site_admin', True),
        ('nosite_staff', False),
    ])
    def test_multiple_user_orgs(self, username, allow):
        """
        Allow users to have multiple orgs.

        Probably we'll remove this features, but this ensures Tahoe doesn't go crazy.
        """
        self.request.user = get_user_model().objects.get(username=username)
        org2 = OrganizationFactory(sites=[self.site])
        UserOrganizationMapping.objects.create(user=self.request.user, organization=org2),
        permission = IsSiteAdminUser().has_permission(self.request, None)
        assert permission == allow, 'Incorrect permission for user: "{username}"'.format(username=username)
