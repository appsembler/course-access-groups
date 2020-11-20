# -*- coding: utf-8 -*-
"""
Tests for the CAG API ViewSets.
"""


import pytest

from course_access_groups.views import CourseAccessGroupViewSet
from course_access_groups.permissions import CommonAuthMixin

from test_utils import get_api_view_classes


class TestCommonAuthMixinUsage(object):
    """
    Ensure the CommonAuthMixin is used by APIs.
    """

    def test_sanity_check(self):
        """
        Ensure that `api_view_classes` contains the correct classes.

        A sanity check just in case the `get_api_view_classes` helper is incorrect.
        """
        api_view_classes = get_api_view_classes()
        assert api_view_classes, 'View classes are being found correctly.'
        assert CourseAccessGroupViewSet in api_view_classes

    @pytest.mark.parametrize('api_view_class', get_api_view_classes())
    def test_common_auth_mixin_used(self, api_view_class):
        """
        Ensure CommonAuthMixin is used on all API ViewSets.

        :param api_view_class: An API view class e.g. MembershipRuleViewSet

        `get_api_view_classes()` auto discovers the following views:
         - CourseAccessGroupViewSet
         - MemberViewSet
         - MembershipRuleViewSet
         - GroupCourseViewSet
         - in addition to any other future class
        """
        assert issubclass(api_view_class, CommonAuthMixin), 'Permissions: {cls} should inherit from {parent}'.format(
            cls=api_view_class.__name__,
            parent=CommonAuthMixin.__name__,
        )
