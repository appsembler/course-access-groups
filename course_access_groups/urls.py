# -*- coding: utf-8 -*-
"""
URLs for course_access_groups.
"""
from __future__ import absolute_import, unicode_literals

from django.conf.urls import include, url
from rest_framework import routers

from course_access_groups import views


router = routers.DefaultRouter()

router.register(
    r'groups',
    views.GroupsViewSet,
    base_name='groups',
)


urlpatterns = [
    url(r'^api/course_access_groups/v1/', include(router.urls, namespace='course-access-groups-api')),
]
