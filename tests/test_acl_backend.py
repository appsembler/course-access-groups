# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import six
import pytest
from test_utils.factories import (
    UserFactory,
    CourseAccessGroupFactory,
    CourseOverviewFactory,
    MembershipFactory,
    OrganizationFactory,
    GroupCourseFactory,
)
from organizations.models import OrganizationCourse, UserOrganizationMapping
from course_access_groups.acl_backends import default_backend
from test_utils import patch_site_configs

@pytest.mark.django_db
class TestAclBackend(object):
    """
    Tests for the access control backend.

    Testing the integration point with Open edX.

    Platforms' `default_has_access` is always checked via this backend.
    """

    @pytest.fixture(autouse=True)
    def init_models(self):
        """
        Create test model fixtures.
        """
        self.user = UserFactory.create()
        self.course = CourseOverviewFactory.create()

    @pytest.mark.parametrize('default_has_access', [False, True])
    def test_blocked_by_default(self, default_has_access):
        """
        Ensure that a learner without a CAG Group has arbitrary access.

        When the feature is enabled, the platform access rules (default_has_access) are ignored.

        :param default_has_access: Experimenting with different Access Control Backends `default_has_access` parameter.
        :return:
        """
        assert not default_backend(self.user, self.course, default_has_access, {})

    @pytest.mark.parametrize('default_has_access', [False, True])
    def test_disabled_feature(self, default_has_access):
        """
        When the feature is disabled, the platform access rules (default_has_access) are applied.

        :param default_has_access: Experimenting with different Access Control Backends `default_has_access` parameter.
        """
        with patch_site_configs({'ENABLE_COURSE_ACCESS_GROUPS': False}):
            assert default_backend(self.user, self.course, default_has_access, {}) == default_has_access

    @pytest.mark.parametrize('default_has_access', [False, True])
    def test_admins_have_access(self, default_has_access):
        """
        Staff and Superusers access is controlled by the platform `default_has_access`.
        """
        staff = UserFactory.create(is_staff=True)
        superuser = UserFactory.create(is_superuser=True)
        assert default_backend(staff, self.course, default_has_access, {}) == default_has_access
        assert default_backend(superuser, self.course, default_has_access, {}) == default_has_access

    @pytest.mark.parametrize('default_has_access', [False, True])
    def test_org_admins_have_access(self, default_has_access):
        """
        Organization-wide admins have access to all org courses.
        """
        user = UserFactory.create()
        organization=OrganizationFactory.create()
        OrganizationCourse.objects.create(course_id=six.text_type(self.course.id), organization=organization)
        UserOrganizationMapping.objects.create(
            user=user,
            organization=organization,
            is_amc_admin=True,
        )
        assert default_backend(user, self.course, default_has_access, {}) == default_has_access

    @pytest.mark.parametrize('default_has_access', [False, True])
    def test_allow_members(self, default_has_access):
        """
        Members have access to courses.

        Via the `Membership` whether it's automatic via `MembershipRule` or manually assigned.
        """
        group = CourseAccessGroupFactory.create()
        GroupCourseFactory.create(course=self.course, group=group)
        MembershipFactory.create(user=self.user, group=group)
        assert default_backend(self.user, self.course, default_has_access, {}) == default_has_access
