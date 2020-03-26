"""
DRF ViewSet filters.
"""

import django_filters
from django.contrib.auth import get_user_model


class UserFilter(django_filters.FilterSet):
    email_exact = django_filters.CharFilter(name='email', lookup_expr='iexact')
    group = django_filters.NumberFilter(name='membership__group_id')
    no_group = django_filters.BooleanFilter(name='membership__id', lookup_expr='isnull')

    class Meta:
        model = get_user_model()
        fields = ['group', 'no_group']
