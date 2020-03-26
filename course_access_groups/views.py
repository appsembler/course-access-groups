# -*- coding: utf-8 -*-
"""
API Endpoints for Course Access Groups.
"""

from __future__ import absolute_import, unicode_literals


from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from opaque_keys.edx.keys import CourseKey
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from organizations.models import OrganizationCourse, UserOrganizationMapping
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from course_access_groups.filters import (
    CourseOverviewFilter,
    UserFilter,
)
from course_access_groups.serializers import (
    CourseAccessGroupSerializer,
    CourseOverviewSerializer,
    MembershipSerializer,
    MembershipRuleSerializer,
    GroupCourseSerializer,
    PublicCourseSerializer,
    UserSerializer,
)
from course_access_groups.models import (
    CourseAccessGroup,
    Membership,
    MembershipRule,
    GroupCourse,
    PublicCourse,
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


class CourseViewSet(CommonAuthMixin, viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet to retrieve courses information with their Course Access Group associations.

    This ViewSet is provide only the minimal course information like id and name.
    For more detailed course information other specialised APIs should be used.
    """

    model = CourseOverview
    pagination_class = LimitOffsetPagination
    serializer_class = CourseOverviewSerializer
    lookup_url_kwarg = 'pk'
    filter_class = CourseOverviewFilter
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['id', 'display_name']

    def get_object(self):
        """
        Override the GenericAPIView.get_object to fix CourseKey related issue.
        """
        course_key = CourseKey.from_string(self.kwargs[self.lookup_url_kwarg])
        self.kwargs[self.lookup_url_kwarg] = course_key
        return super(CourseViewSet, self).get_object()

    def get_queryset(self):
        organization = get_current_organization(self.request)
        return CourseOverview.objects.filter(
            id__in=OrganizationCourse.objects.filter(
                organization=organization,
                active=True,
            ).values('course_id'),
        )


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


class PublicCourseViewSet(CommonAuthMixin, viewsets.ModelViewSet):
    """
    API ViewSet to mark specific courses as public to circumvent the Course Access Group rules.
    """

    model = PublicCourse
    pagination_class = LimitOffsetPagination
    serializer_class = PublicCourseSerializer

    def get_queryset(self):
        organization = get_current_organization(self.request)
        course_links = OrganizationCourse.objects.filter(organization=organization, active=True)

        return self.model.objects.filter(
            course_id__in=course_links.values('course_id'),
        )


class UserViewSet(CommonAuthMixin, viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet to retrieve user information with their Course Access Group associations.

    This ViewSet is provide only the minimal user information like email and username.
    For more detailed user information other specialised APIs should be used.
    """

    model = get_user_model()
    pagination_class = LimitOffsetPagination
    serializer_class = UserSerializer
    filter_class = UserFilter
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['email', 'username', 'profile__name']

    def get_queryset(self):
        organization = get_current_organization(self.request)
        return self.model.objects.filter(
            pk__in=UserOrganizationMapping.objects.filter(
                organization=organization,
                is_active=True,  # TODO: Add test for `is_active`
                is_amc_admin=False,  # Site admins shouldn't be included in the API.
            ).values('user_id'),
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
