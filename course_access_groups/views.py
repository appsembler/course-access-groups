# -*- coding: utf-8 -*-
"""
Views for course_access_groups.
"""

from __future__ import absolute_import, unicode_literals

from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination


from course_access_groups.serializers import GroupSerializer
from course_access_groups.models import (
    CourseAccessGroup,
)


class GroupsViewSet(viewsets.ModelViewSet):
    model = CourseAccessGroup
    pagination_class = LimitOffsetPagination
    serializer_class = GroupSerializer

    def get_queryset(self):
        return CourseAccessGroup.objects.all()
