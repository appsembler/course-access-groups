# -*- coding: utf-8 -*-
"""
Testing the Access Control Backend `acl_backend.user_has_access`.
"""


import pytest
from django.contrib.auth.models import AnonymousUser
from organizations.models import OrganizationCourse
from tahoe_sites.tests.utils import create_organization_mapping

from course_access_groups.acl_backends import user_has_access
from course_access_groups.openedx_modules import ACCESS_DENIED, ACCESS_GRANTED
from test_utils import patch_site_configs
from test_utils.factories import (
    CourseAccessGroupFactory,
    CourseOverviewFactory,
    GroupCourseFactory,
    MembershipFactory,
    OrganizationFactory,
    PublicCourseFactory,
    UserFactory
)


@pytest.mark.django_db
class TestAclBackend:
    """
    Tests for the access control backend.

    Testing the integration point with Open edX.

    Platforms' `default_has_access` is always checked via this backend.

    TODO: Simplify most of the integration tests below into unit tests for
          the `permissions.user_has_access_to_course` helper.
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """
        Create test model fixtures.
        """
        self.user = UserFactory.create()
        self.course = CourseOverviewFactory.create()

    @pytest.mark.parametrize('default_has_access', [ACCESS_DENIED, ACCESS_GRANTED])
    def test_blocked_by_default(self, default_has_access):
        """
        Ensure that a learner without a CAG Group has arbitrary access.

        When the feature is enabled, the platform access rules (default_has_access) are ignored.

        :param default_has_access: Experimenting with different Access Control Backends `default_has_access` parameter.
        :return:
        """
        assert not user_has_access(self.user, self.course, default_has_access, {})

    @pytest.mark.parametrize('default_has_access', [ACCESS_DENIED, ACCESS_GRANTED])
    def test_disabled_feature(self, default_has_access):
        """
        When the feature is disabled, the platform access rules (default_has_access) are applied.

        :param default_has_access: Experimenting with different Access Control Backends `default_has_access` parameter.
        """
        with patch_site_configs({'ENABLE_COURSE_ACCESS_GROUPS': False}):
            assert user_has_access(self.user, self.course, default_has_access, {}) == default_has_access

    @pytest.mark.parametrize('default_has_access', [ACCESS_DENIED, ACCESS_GRANTED])
    def test_site_staff_have_access(self, default_has_access):
        """
        Site-wide staff access is controlled by the platform `default_has_access`.
        """
        staff = UserFactory.create(is_staff=True)
        assert user_has_access(staff, self.course, default_has_access, {}) == default_has_access

    @pytest.mark.parametrize('default_has_access', [ACCESS_DENIED, ACCESS_GRANTED])
    def test_superuser_have_access(self, default_has_access):
        """
        Superusers access is controlled by the platform `default_has_access`.
        """
        superuser = UserFactory.create(is_superuser=True)
        assert user_has_access(superuser, self.course, default_has_access, {}) == default_has_access

    @pytest.mark.parametrize('default_has_access', [ACCESS_DENIED, ACCESS_GRANTED])
    def test_org_admins_have_access(self, default_has_access):
        """
        Organization-wide admins have access to all org courses.
        """
        user = UserFactory.create()
        organization = OrganizationFactory.create()
        OrganizationCourse.objects.create(course_id=str(self.course.id), organization=organization)
        create_organization_mapping(
            user=user,
            organization=organization,
            is_admin=True,
        )
        assert user_has_access(user, self.course, default_has_access, {}) == default_has_access

        # Basic test for `is_organization_staff` to ensure `user.is_active` is respected.
        inactive = UserFactory.create(is_active=False)
        assert not user_has_access(inactive, self.course, default_has_access, {})

    @pytest.mark.parametrize('default_has_access', [ACCESS_DENIED, ACCESS_GRANTED])
    def test_allow_members(self, default_has_access):
        """
        Members have access to courses.

        Via the `Membership` whether it's automatic via `MembershipRule` or manually assigned.
        """
        group = CourseAccessGroupFactory.create()
        GroupCourseFactory.create(course=self.course, group=group)
        MembershipFactory.create(user=self.user, group=group)
        assert user_has_access(self.user, self.course, default_has_access, {}) == default_has_access

    @pytest.mark.parametrize('default_has_access', [ACCESS_DENIED, ACCESS_GRANTED])
    def test_disallow_anonymous_user(self, default_has_access):
        """
        AnonymousUser don't have access to private courses.
        """
        user = AnonymousUser()
        assert not user_has_access(user, self.course, default_has_access, {})

    @pytest.mark.parametrize('default_has_access', [ACCESS_DENIED, ACCESS_GRANTED])
    def test_allow_public_courses(self, default_has_access):
        """
        Public courses should be allowed to non-members.

        Via the `PublicCourse` model.
        """
        org = OrganizationFactory.create()
        OrganizationCourse.objects.create(course_id=str(self.course.id), organization=org)
        create_organization_mapping(
            user=self.user,
            organization=org,
        )
        PublicCourseFactory.create(course=self.course)
        assert user_has_access(self.user, self.course, default_has_access, {}) == default_has_access
