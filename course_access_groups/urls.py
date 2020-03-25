# -*- coding: utf-8 -*-
"""
URLs for course_access_groups.
"""
from __future__ import absolute_import, unicode_literals

from rest_framework import routers
from course_access_groups import views


router = routers.SimpleRouter()

router.register(
    r'courses',
    views.CourseViewSet,
    base_name='courses',
)

router.register(
    r'course-access-groups',
    views.CourseAccessGroupViewSet,
    base_name='course-access-groups',
)

router.register(
    r'memberships',
    views.MembershipViewSet,
    base_name='memberships',
)

router.register(
    r'membership-rules',
    views.MembershipRuleViewSet,
    base_name='membership-rules',
)

router.register(
    r'public-courses',
    views.PublicCourseViewSet,
    base_name='public-courses',
)

router.register(
    r'users',
    views.UserViewSet,
    base_name='users',
)

router.register(
    r'group-courses',
    views.GroupCourseViewSet,
    base_name='group-courses',
)

urlpatterns = router.urls
