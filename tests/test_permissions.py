# -*- coding: utf-8 -*-
"""
Test the authentication and permission of Course Access Groups.
"""


import pytest
from django.contrib.auth import get_user_model
from django.contrib.sites import shortcuts as sites_shortcuts
from django.core.exceptions import MultipleObjectsReturned
from mock import Mock, patch
from openedx.core.lib.api.authentication import OAuth2Authentication
from organizations.models import Organization, OrganizationCourse
from rest_framework.authentication import TokenAuthentication
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import PermissionDenied
from tahoe_sites.api import (
    create_tahoe_site,
    get_current_organization,
    get_uuid_by_organization,
)
from tahoe_sites.tests.utils import create_organization_mapping

from course_access_groups.permissions import (
    CommonAuthMixin,
    IsSiteAdminUser,
    get_requested_organization,
    is_active_staff_or_superuser,
    is_course_with_public_access,
    is_organization_staff,
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


@pytest.mark.django_db
class TestGetRequestedOrganization:
    """
    Tests for get_requested_organization.
    """

    def test_on_customer_site(self):
        """
        Customer sites can use CAG APIs.
        """
        expected_info = create_tahoe_site(domain='my_site.org', short_name='any')

        non_superuser = UserFactory.create()
        request = Mock(site=expected_info['site'], user=non_superuser, GET={})

        requested_org = get_requested_organization(request)
        assert requested_org == expected_info['organization'], 'Should return the site organization'

    def test_on_main_site_with_uuid_parameter(self, settings):
        """
        Superusers can use the `get_requested_organization` helper with `organization_uuid`.
        """
        main_site = SiteFactory.create(domain='main_site')
        settings.SITE_ID = main_site.id

        customer_org = create_tahoe_site(domain='customer_site', short_name='any')['organization']

        superuser = UserFactory.create(is_superuser=True)
        request = Mock(site=main_site, user=superuser, GET={
            'organization_uuid': get_uuid_by_organization(customer_org),
        })

        requested_org = get_requested_organization(request)
        assert requested_org == customer_org, 'Should return the site organization'

    def test_on_main_site_without_uuid_parameter(self, settings):
        """
        Non superusers shouldn't use the CAG on main site ( e.g. tahoe.appsembler.com/admin ).
        """
        main_site = SiteFactory.create(domain='main_site')
        settings.SITE_ID = main_site.id

        create_tahoe_site(domain='customer_site', short_name='any')
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

        customer_org = create_tahoe_site(domain='customer_site', short_name='any')['organization']
        non_superuser = UserFactory.create()
        request = Mock(site=main_site, user=non_superuser, GET={
            'organization_uuid': get_uuid_by_organization(customer_org),
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
        info = create_tahoe_site(domain='testdomain.org', short_name='TD')
        self.organization = info['organization']
        self.site = info['site']

        self.callers = [
            UserFactory.create(username='alpha_nonadmin'),
            UserFactory.create(username='alpha_site_admin'),
            UserFactory.create(username='nosite_staff'),
        ]
        self.user_organization_mappings = [
            create_organization_mapping(
                user=self.callers[0],
                organization=self.organization),
            create_organization_mapping(
                user=self.callers[1],
                organization=self.organization,
                is_admin=True)
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
class TestOrganizationStaffHelper:
    """
    Tests for permissions.is_organization_staff
    """
    def setup(self):
        self.user = UserFactory.create()
        self.org1 = OrganizationFactory.create()
        self.org2 = OrganizationFactory.create()
        self.course = CourseOverviewFactory.create()
        OrganizationCourse.objects.create(course_id=str(self.course.id), organization=self.org1)
        create_organization_mapping(
            user=self.user,
            organization=self.org1,
            is_admin=True,
        )

    def test_admin_user(self):
        """
        Verify that is_organization_staff returns True if the user is an admin on the course's organization
        """
        assert is_organization_staff(self.user, self.course)

    def test_non_admin_user(self):
        """
        Verify that is_organization_staff returns False if the user is an admin on the course's organization
        """
        user2 = UserFactory.create()
        create_organization_mapping(
            user=user2,
            organization=self.org1,
            is_admin=False,
        )
        assert not is_organization_staff(user2, self.course)

    def test_multi_org_course(self):
        """
        Verify that is_organization_staff returns False if there are many active organization-course links
        for the same course
        """
        with patch(
            'course_access_groups.permissions.get_organization_by_course',
            side_effect=MultipleObjectsReturned()
        ):
            with patch('course_access_groups.permissions.log.warning') as mock_log:
                assert not is_organization_staff(self.user, self.course)
                mock_log.assert_called_with(
                    'Course Access Group: This module expects a one:one relationship between'
                    ' organizations and course. Raised by course (%s)', self.course.id
                )

    def test_course_org_not_related_to_user(self):
        """
        Verify that is_organization_staff will return False if the user is not related to the same organization
        of the course
        """
        with patch(
            'course_access_groups.permissions.get_organization_by_course',
            side_effect=Organization.DoesNotExist()
        ):
            with patch('course_access_groups.permissions.log.warning') as mock_log:
                assert not is_organization_staff(Mock(), self.course)
                assert mock_log.call_count == 0


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
