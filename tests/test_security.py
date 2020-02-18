# -*- coding: utf-8 -*-
"""
Test the authentication and permission of Course Access Groups.
"""

import pytest

from django.contrib.auth import get_user_model

import django.contrib.sites.shortcuts

from rest_framework.test import APIRequestFactory

from organizations.models import UserOrganizationMapping

from test_utils.factories import OrganizationFactory, UserFactory, create_standard_test_users


@pytest.mark.django_db
class TestOrgAdminPermission(object):

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.organization = OrganizationFactory()
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

    @pytest.mark.parametrize('username, allow', [
        ('regular_user', False),
        ('staff_user', True),
        ('super_user', True),
        ('superstaff_user', True),
        ('alpha_nonadmin', False),
        ('alpha_site_admin', True),
        ('nosite_staff', False),
    ])
    def test_is_site_admin_user(self, monkeypatch, settings, username, allow):
        request = APIRequestFactory().get('/')
        # request.META['HTTP_HOST'] = self.site.domain
        request.user = get_user_model().objects.get(username=username)
        permission = IsSiteAdminUser().has_permission(
            request, None)
        assert permission is allow, 'User "{username}" should have access'.format(
            username=username)

        # verify that inactive users are denied permission
        request.user.is_active = False
        permission = IsSiteAdminUser().has_permission(
            request, None)
        assert permission is False, 'username: "{username}"'.format(
            username=username)

    def test_multiple_user_orgs(self):
        def test_site(request):
            return self.site
        username = 'alpha_site_admin'
        request = APIRequestFactory().get('/')
        request.META['HTTP_HOST'] = self.site.domain
        request.user = get_user_model().objects.get(username=username)
        org2 = OrganizationFactory(sites=[self.site])
        UserOrganizationMapping.objects.create(user=request.user, organization=org2),
        with pytest.raises(figures.permissions.MultipleOrgsPerUserNotSupported):
            figures.permissions.IsSiteAdminUser().has_permission(request, None)
