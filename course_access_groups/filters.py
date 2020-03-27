"""
DRF ViewSet filters.
"""

import django_filters
from django.contrib.auth import get_user_model

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview


class UserFilter(django_filters.FilterSet):
    email_exact = django_filters.CharFilter(name='email', lookup_expr='iexact')
    group = django_filters.NumberFilter(name='membership__group_id')
    no_group = django_filters.BooleanFilter(name='membership__id', lookup_expr='isnull')

    class Meta:
        model = get_user_model()
        fields = ['email_exact', 'group', 'no_group']


class CourseOverviewFilter(django_filters.FilterSet):
    group = django_filters.NumberFilter(name='group_courses__group_id')
    no_group = django_filters.BooleanFilter(name='group_courses', lookup_expr='isnull')
    is_public = django_filters.BooleanFilter(name='public_course', lookup_expr='isnull', exclude=True)

    class Meta:
        model = CourseOverview
        fields = ['group', 'no_group', 'is_public']
