# -*- coding: utf-8 -*-
"""
API Endpoints for Course Access Groups.
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
from course_access_groups.permissions import get_current_organization, CommonAuthMixin


class CourseAccessGroupViewSet(CommonAuthMixin, viewsets.ModelViewSet):
    """REST API endpoints to manage Course Access Groups.

    These endpoints follows the standard Django Rest Framework ViewSet API structure.

    GET /course-access-groups/
    """

    model = CourseAccessGroup
    pagination_class = LimitOffsetPagination
    serializer_class = CourseAccessGroupSerializer

    def perform_create(self, serializer):
        organization = get_current_organization(self.request)
        serializer.save(organization=organization)

    def get_queryset(self):
        organization = get_current_organization(self.request)
        return self.model.objects.filter(organization=organization)


class MembershipViewSet(CommonAuthMixin, viewsets.ModelViewSet):
    model = Membership
    pagination_class = LimitOffsetPagination
    serializer_class = MembershipSerializer

    def get_queryset(self):
        organization = get_current_organization(self.request)
        return self.model.objects.filter(
            group__in=CourseAccessGroup.objects.filter(organization=organization),
        )


class MembershipRuleViewSet(CommonAuthMixin, viewsets.ModelViewSet):
    model = MembershipRule
    pagination_class = LimitOffsetPagination
    serializer_class = MembershipRuleSerializer

    def get_queryset(self):
        organization = get_current_organization(self.request)
        return self.model.objects.filter(
            group__in=CourseAccessGroup.objects.filter(organization=organization),
        )


class GroupCourseViewSet(CommonAuthMixin, viewsets.ModelViewSet):
    model = GroupCourse
    pagination_class = LimitOffsetPagination
    serializer_class = GroupCourseSerializer

    def get_queryset(self):
        organization = get_current_organization(self.request)
        return self.model.objects.filter(
            group__in=CourseAccessGroup.objects.filter(organization=organization),
        )
