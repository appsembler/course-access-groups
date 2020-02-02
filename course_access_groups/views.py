# -*- coding: utf-8 -*-
"""
Views for course_access_groups.
"""

from __future__ import absolute_import, unicode_literals


from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination

from course_access_groups.serializers import (
    GroupSerializer,
    MembershipSerializer,
    RuleSerializer,
    CourseGroupSerializer,
)
from course_access_groups.models import (
    Group,
    Membership,
    Rule,
    CourseGroup,
)


class GroupViewSet(viewsets.ModelViewSet):
    model = Group
    pagination_class = LimitOffsetPagination
    serializer_class = GroupSerializer

    def get_queryset(self):
        return self.model.objects.all()


class MemberViewSet(viewsets.ModelViewSet):
    model = Membership
    pagination_class = LimitOffsetPagination
    serializer_class = MembershipSerializer

    def get_queryset(self):
        return self.model.objects.all()


class RuleViewSet(viewsets.ModelViewSet):
    model = Rule
    pagination_class = LimitOffsetPagination
    serializer_class = RuleSerializer

    def get_queryset(self):
        return self.model.objects.all()


class CourseGroupViewSet(viewsets.ModelViewSet):
    model = CourseGroup
    pagination_class = LimitOffsetPagination
    serializer_class = CourseGroupSerializer

    def get_queryset(self):
        return self.model.objects.all()
