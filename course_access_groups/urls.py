# -*- coding: utf-8 -*-
"""
URLs for course_access_groups.
"""
from __future__ import absolute_import, unicode_literals

from rest_framework import routers
from course_access_groups import views


router = routers.SimpleRouter()

router.register(
    r'groups',
    views.GroupViewSet,
    base_name='groups',
)

router.register(
    r'memberships',
    views.MemberViewSet,
    base_name='memberships',
)

router.register(
    r'rules',
    views.RuleViewSet,
    base_name='rules',
)

router.register(
    r'course-groups',
    views.CourseGroupViewSet,
    base_name='course-groups',
)

urlpatterns = router.urls
