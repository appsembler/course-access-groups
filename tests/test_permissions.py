# -*- coding: utf-8 -*-
"""
Test the authentication and permission of Course Access Groups.
"""


import pytest
from django.contrib.auth import get_user_model
from django.contrib.sites import shortcuts as sites_shortcuts
from mock import Mock, patch
from openedx.core.lib.api.authentication import OAuth2Authentication
from organizations.models import Organization, UserOrganizationMapping
from rest_framework.authentication import TokenAuthentication
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import PermissionDenied

from course_access_groups.permissions import (
    CommonAuthMixin,
    IsSiteAdminUser,
    get_current_organization,
    get_current_site,
    get_requested_organization,
    is_active_staff_or_superuser,
    is_course_with_public_access,
)
from test_utils.factories import (
    CourseOverviewFactory,
    OrganizationFactory,
    PublicCourseFactory,
    SiteFactory,
    UserFactory
)


@pytest.mark.django_db
class TestCurrentOrgHelper:
    def test_no_site(self):
        """
        Ensure no sites are handled properly.
        """
        request = Mock(site=None)
        with pytest.raises(Organization.DoesNotExist):
            get_current_organization(request)

    def test_no_organization(self):
        """
        Ensure no orgs are handled properly.
        """
        site = SiteFactory.create(domain='my_site.org')
        request = Mock(site=site)
        with pytest.raises(Organization.DoesNotExist,
                           match=r'Organization matching query does not exist'):
            get_current_organization(request)

    def test_organization_main_site(self, settings):
        """
        Ensure no orgs are handled properly.
        """
        site = SiteFactory.create(domain='my_site.org')
        settings.SITE_ID = site.id
        request = Mock(site=site)
        with pytest.raises(Organization.DoesNotExist, match=r'Tahoe.*Should not find.*SITE_ID'):
            get_current_organization(request)

    def test_two_organizations(self):
        """
        Ensure multiple orgs to be forbidden.
        """
        site = SiteFactory.create(domain='my_site.org')
        OrganizationFactory.create_batch(2, sites=[site])
        request = Mock(site=site)

        with pytest.raises(Organization.MultipleObjectsReturned):
            get_current_organization(request)

    def test_single_organization(self):
        """
        Ensure multiple orgs to be forbidden.
        """
        my_site = SiteFactory.create(domain='my_site.org')
        other_site = SiteFactory.create(domain='other_site.org')  # ensure no collision.
        my_org = OrganizationFactory.create(sites=[my_site])
        OrganizationFactory.create(sites=[other_site])  # ensure no collision.
        request = Mock(site=my_site)
        assert my_org == get_current_organization(request)


@pytest.mark.django_db
class TestGetRequestedOrganization:
    """
    Tests for get_requested_organization.
    """

    def test_on_customer_site(self):
        """
        Customer sites can use CAG APIs.
        """
        site = SiteFactory.create(domain='my_site.org')
        expected_org = OrganizationFactory.create(sites=[site])
        non_superuser = UserFactory.create()
        request = Mock(site=site, user=non_superuser, GET={})

        requested_org = get_requested_organization(request)
        assert requested_org == expected_org, 'Should return the site organization'

    def test_on_main_site_with_uuid_parameter(self, settings):
        """
        Superusers can use the `get_requested_organization` helper with `organization_uuid`.
        """
        main_site = SiteFactory.create(domain='main_site')
        settings.SITE_ID = main_site.id

        customer_site = SiteFactory.create(domain='customer_site')
        customer_org = OrganizationFactory.create(sites=[customer_site])
        superuser = UserFactory.create(is_superuser=True)
        request = Mock(site=main_site, user=superuser, GET={
            'organization_uuid': customer_org.edx_uuid,
        })

        requested_org = get_requested_organization(request)
        assert requested_org == customer_org, 'Should return the site organization'

    def test_on_main_site_without_uuid_parameter(self, settings):
        """
        Non superusers shouldn't use the CAG on main site ( e.g. tahoe.appsembler.com/admin ).
        """
        main_site = SiteFactory.create(domain='main_site')
        settings.SITE_ID = main_site.id

        customer_site = SiteFactory.create(domain='customer_site')
        OrganizationFactory.create(sites=[customer_site])  # Creates customer_org
        superuser = UserFactory.create(is_superuser=True)
        request = Mock(site=main_site, user=superuser, GET={})

        with pytest.raises(Organization.DoesNotExist,
                           match=r'Tahoe.*Should not find.*SITE_ID'):
            get_requested_organization(request)

    def test_on_main_site_with_uuid_parameter_non_staff(self, settings):
        """
        Non superusers shouldn't be able to use the `organization_uuid` parameters.
        """
        main_site = SiteFactory.create(domain='main_site')
        settings.SITE_ID = main_site.id

        customer_site = SiteFactory.create(domain='customer_site')
        customer_org = OrganizationFactory.create(sites=[customer_site])
        non_superuser = UserFactory.create()
        request = Mock(site=main_site, user=non_superuser, GET={
            'organization_uuid': customer_org.edx_uuid,
        })

        with pytest.raises(PermissionDenied,
                           match=r'Not permitted to use the `organization_uuid` parameter.'):
            get_requested_organization(request)


@pytest.mark.django_db
class TestSiteAdminPermissions:
    """
    Test for the IsSiteAdminUser permission class.
    """

    @pytest.fixture(autouse=True)
    def setup(self, db, monkeypatch, standard_test_users):
        self.site = SiteFactory.create()
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
        self.request.site = self.site
        monkeypatch.setattr(sites_shortcuts, 'get_current_site', self.get_test_site)

    def get_test_site(self, request):
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
class TestStaffSuperuserHelper:
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
    def test_active_user(self, standard_test_users, username, allow):
        user = get_user_model().objects.get(username=username)
        assert is_active_staff_or_superuser(user) == allow

    @pytest.mark.parametrize('username', [
        'regular_user',
        'staff_user',
        'super_user',
        'superstaff_user',
    ])
    def test_inactive_user(self, standard_test_users, username):
        user = get_user_model().objects.get(username=username)
        user.is_active = False
        assert not is_active_staff_or_superuser(user)


@pytest.mark.django_db
class TestIsCourseWithPublicAccessHelper:
    """
    Tests for the permissions.is_course_with_public_access helper.
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        self.my_course = CourseOverviewFactory.create()

    def test_courses_not_public_by_default(self):
        assert not is_course_with_public_access(self.my_course)

    def test_access_for_public_courses(self):
        PublicCourseFactory.create(course=self.my_course)
        assert is_course_with_public_access(self.my_course)

    def test_with_course_descriptor(self):
        """
        Test when CourseDescriptorWithMixins is passed instead of CourseOverview.

        Warning: This is a somewhat complex test case due to the inherent complexity with CourseDescriptorWithMixins
                 class in Open edX. If it breaks and it took a lot of time to fix, please consider removing it
                 and relying on manual testing instead.
        """
        PublicCourseFactory.create(course=self.my_course)
        course_descriptor = Mock()  # Anything other than CourseOverview
        course_descriptor.id = self.my_course.id

        with patch('django.db.models.sql.query.check_rel_lookup_compatibility', return_value=False):
            assert is_course_with_public_access(course=course_descriptor)


class TestCommonAuthMixin:
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


def test_get_current_site_no_site():
    """
    Emulate the behaviour of `openedx.core.djangoapps.theming.helpers.get_current_site`.
    """
    request = Mock(site=None)
    assert not get_current_site(request)


def test_get_current_site_with_site():
    """
    Emulate the behaviour of `openedx.core.djangoapps.theming.helpers.get_current_site`.
    """
    request = Mock(site={'domain': 'test.org'})
    assert get_current_site(request)
