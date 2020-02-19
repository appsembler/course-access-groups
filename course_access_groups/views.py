# -*- coding: utf-8 -*-
"""
Views for course_access_groups.
"""

from __future__ import absolute_import, unicode_literals


from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination

from course_access_groups.serializers import (
    CourseAccessGroupSerializer,
    MembershipSerializer,
    MembershipRuleSerializer,
    GroupCourseSerializer,
)
from course_access_groups.models import (
    CourseAccessGroup,
    Membership,
    MembershipRule,
    GroupCourse,
)
from course_access_groups.permissions import CommonAuthMixin


class CourseAccessGroupViewSet(CommonAuthMixin, viewsets.ModelViewSet):
    model = CourseAccessGroup
    pagination_class = LimitOffsetPagination
    serializer_class = CourseAccessGroupSerializer

    def get_queryset(self):
        return self.model.objects.all()


class MemberViewSet(CommonAuthMixin, viewsets.ModelViewSet):
    model = Membership
    pagination_class = LimitOffsetPagination
    serializer_class = MembershipSerializer

    def get_queryset(self):
        return self.model.objects.all()


class MembershipRuleViewSet(CommonAuthMixin, viewsets.ModelViewSet):
    model = MembershipRule
    pagination_class = LimitOffsetPagination
    serializer_class = MembershipRuleSerializer

    def get_queryset(self):
        return self.model.objects.all()


class GroupCourseViewSet(CommonAuthMixin, viewsets.ModelViewSet):
    model = GroupCourse
    pagination_class = LimitOffsetPagination
    serializer_class = GroupCourseSerializer

    def get_queryset(self):
        return self.model.objects.all()
