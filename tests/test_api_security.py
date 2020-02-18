# -*- coding: utf-8 -*-
"""
Tests for the CAG API ViewSets.
"""

from __future__ import absolute_import, unicode_literals

from course_access_groups.models import (
    CourseAccessGroup,
    GroupCourse,
    Membership,
    MembershipRule,
)
import pytest
from test_utils.factories import (
    UserFactory,
    CourseAccessGroupFactory,
    CourseOverviewFactory,
    MembershipFactory,
    OrganizationFactory,
    MembershipRuleFactory,
    GroupCourseFactory,
)
from test_utils import skip_authentication, skip_permission


@pytest.mark.django_db
@skip_authentication()
@skip_permission()
class TestCourseAccessGroupsViewSet(object):
    """
    Tests for the CourseAccessGroupsViewSet APIs.
    """


class TestTodo(object):
    todo = True

    def test_todo(self):
        assert False, 'TODO: All API viewsets to use CommonAuthMixin.'
        assert False, 'TODO: CommonAuthMixin to have IsSiteAdminUser.'
        assert False, 'TODO: ViewSets to receive implicit org user based on get_current_request.'
        assert False, 'TODO: ViewSets.get_queryset to respect the org based on get_current_request'
