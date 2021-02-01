# -*- coding: utf-8 -*-
"""
URLs for course_access_groups.
"""


from rest_framework import routers

from course_access_groups import views

router = routers.SimpleRouter()

router.register(
    r'courses',
    views.CourseViewSet,
    basename='courses',
)

router.register(
    r'course-access-groups',
    views.CourseAccessGroupViewSet,
    basename='course-access-groups',
)

router.register(
    r'memberships',
    views.MembershipViewSet,
    basename='memberships',
)

router.register(
    r'membership-rules',
    views.MembershipRuleViewSet,
    basename='membership-rules',
)

router.register(
    r'public-courses',
    views.PublicCourseViewSet,
    basename='public-courses',
)

router.register(
    r'users',
    views.UserViewSet,
    basename='users',
)

router.register(
    r'group-courses',
    views.GroupCourseViewSet,
    basename='group-courses',
)

urlpatterns = router.urls
