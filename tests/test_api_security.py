# -*- coding: utf-8 -*-
"""
Tests for the CAG API ViewSets.
"""

from __future__ import absolute_import, unicode_literals

from django.views import View
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
from course_access_groups import views as cag_views


class TestCourseAccessGroupsViewSet(object):
    """
    Tests for the CourseAccessGroupsViewSet APIs.
    """

    view_classes = [
        variable for variable in [
            getattr(cag_views, var_name)
            for var_name in dir(cag_views)
        ]
        if (isinstance(variable, type) and issubclass(variable, View))
    ]

    def test_sanity_check(self):
        """
        Ensure that `view_classes` contains the correct classes.
        """
        assert self.view_classes, 'View classes are being found correctly.'
        assert cag_views.CourseAccessGroupViewSet in self.view_classes

    @pytest.mark.parametrize('view', view_classes)
    def test_common_auth_mixin_used(self):
        """
        Ensure CommonAuthMixin is used on all API ViewSets.
        """
        assert False


class TestTodo(object):
    todo = True

    def test_todo(self):
        assert False, 'TODO: All API viewsets to use CommonAuthMixin.'
        assert False, 'TODO: CommonAuthMixin to have IsSiteAdminUser.'
        assert False, 'TODO: ViewSets to receive implicit org user based on get_current_request.'
        assert False, 'TODO: ViewSets.get_queryset to respect the org based on get_current_request'
