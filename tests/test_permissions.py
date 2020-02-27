# -*- coding: utf-8 -*-
"""
Test the authentication and permission of Course Access Groups.
"""

from __future__ import absolute_import, unicode_literals

import pytest
from mock import patch, Mock
from django.contrib.auth import get_user_model
from django.contrib.sites import shortcuts as sites_shortcuts
from django.contrib.sites.models import Site
from rest_framework.authentication import TokenAuthentication
from rest_framework.test import APIRequestFactory
from organizations.models import Organization, UserOrganizationMapping
from openedx.core.lib.api.authentication import OAuth2Authentication
from course_access_groups.permissions import (
    is_active_staff_or_superuser,
    get_current_organization,
    CommonAuthMixin,
    IsSiteAdminUser,
)

from test_utils.factories import (
    OrganizationFactory,
    SiteFactory,
    UserFactory,
)


@pytest.mark.django_db
class TestCurrentOrgHelper(object):
    def test_no_site(self):
        """
        Ensure no sites are handled properly.
        """
        request = Mock(get_host=Mock(return_value='my_site.org'))
        with pytest.raises(Site.DoesNotExist):
            get_current_organization(request)

    def test_no_organization(self):
        """
        Ensure no orgs are handled properly.
        """
        site = SiteFactory(domain='my_site.org')
        request = Mock(get_host=Mock(return_value=site.domain))
        with pytest.raises(Organization.DoesNotExist):
            get_current_organization(request)

    def test_two_organizations(self):
        """
        Ensure multiple orgs to be forbidden.
        """
        site = SiteFactory(domain='my_site.org')
        OrganizationFactory.create_batch(2, sites=[site])
        request = Mock(get_host=Mock(return_value=site.domain))

        with pytest.raises(Organization.MultipleObjectsReturned):
            get_current_organization(request)

    def test_single_organization(self):
        """
        Ensure multiple orgs to be forbidden.
        """
        my_site = SiteFactory(domain='my_site.org')
        other_site = SiteFactory(domain='other_site.org')  # ensure no collision.
        my_org = OrganizationFactory.create(sites=[my_site])
        OrganizationFactory.create(sites=[other_site])  # ensure no collision.
        request = Mock(get_host=Mock(return_value=my_site.domain))
        assert my_org == get_current_organization(request)


@pytest.mark.django_db
class TestSiteAdminPermissions(object):
    """
    Test for the IsSiteAdminUser permission class.
    """

    @pytest.fixture(autouse=True)
    def setup(self, db, monkeypatch, standard_test_users):
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
        self.callers += standard_test_users
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

    @pytest.mark.parametrize('username, allow, log_call_count', [
        ('regular_user', False, 1),
        ('staff_user', True, 0),  # Site-wide staff are exempted from org checks.
        ('super_user', True, 0),  # Superusers are exempted from org checks.
        ('superstaff_user', True, 0),  # Superusers are exempted from org checks.
        ('alpha_nonadmin', False, 1),
        ('alpha_site_admin', False, 1),
        ('nosite_staff', False, 1),
    ])
    def test_multiple_user_orgs(self, username, allow, log_call_count):
        """
        Prevent users from having multiple orgs.
        """
        self.request.user = get_user_model().objects.get(username=username)
        org2 = OrganizationFactory(sites=[self.site])
        UserOrganizationMapping.objects.create(user=self.request.user, organization=org2),

        with patch('course_access_groups.permissions.log') as mock_log:
            permission = IsSiteAdminUser().has_permission(self.request, None)
            assert mock_log.exception.call_count == log_call_count
        assert permission == allow, 'Incorrect permission for user: "{username}"'.format(username=username)


@pytest.mark.django_db
class TestStaffSuperuserHelper(object):
    """
    Tests for permissions.is_active_staff_or_superuser.
    """

    def test_none_user(self):
        assert not is_active_staff_or_superuser(None)

    @pytest.mark.parametrize('username, allow', [
        ('regular_user', False),
        ('staff_user', True),
        ('super_user', True),
        ('superstaff_user', True),
    ])
    def test_active_user(self, standard_test_users, username, allow):  # pylint: disable=unused-argument
        user = get_user_model().objects.get(username=username)
        assert is_active_staff_or_superuser(user) == allow

    @pytest.mark.parametrize('username', [
        'regular_user',
        'staff_user',
        'super_user',
        'superstaff_user',
    ])
    def test_inactive_user(self, standard_test_users, username):  # pylint: disable=unused-argument
        user = get_user_model().objects.get(username=username)
        user.is_active = False
        assert not is_active_staff_or_superuser(user)


class TestCommonAuthMixin(object):
    """
    Tests for CommonAuthMixin.

    This class is minimal because CommonAuthMixin should be tested in `test_api_permissions`.
    """

    @pytest.mark.parametrize('auth_backend, reason', [
        [OAuth2Authentication, 'Should work with Bearer OAuth token from within AMC'],
        [TokenAuthentication, 'Should work with API Token for external usage'],
    ])
    def test_token_authentication(self, auth_backend, reason):
        """
        Ensures that the APIs are usable with an API Token besides the AMC Bearer token.
        """
        assert auth_backend in CommonAuthMixin.authentication_classes, reason

    def test_is_site_admin_user_permission(self):
        """
        Ensures that the APIs are only callable by Site Admin User.
        """
        assert IsSiteAdminUser in CommonAuthMixin.permission_classes, 'Only authorized users may access CAG views'
