# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from six import text_type
from django.contrib.auth import get_user_model

from organizations.models import UserOrganizationMapping, OrganizationCourse
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from course_access_groups.models import (
    CourseAccessGroup,
    GroupCourse,
    Membership,
    MembershipRule,
)
from course_access_groups.permissions import get_current_organization


class CourseKeyField(serializers.RelatedField):
    """
    Serializer field for a model CourseKey field.

    This is copied from the openedx.core.lib.api.serializers module but enhanced with `RelatedField`.
    """

    def get_queryset(self):
        return CourseOverview.objects.values_list('id', flat=True)

    def to_representation(self, data):
        """Convert a course key to unicode. """
        return str(data)

    def to_internal_value(self, data):
        """Convert unicode to a course key. """
        try:
            return CourseKey.from_string(data)
        except InvalidKeyError as ex:
            raise serializers.ValidationError('Invalid course key: {msg}'.format(msg=str(ex)))


class CourseAccessGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseAccessGroup
        fields = [
            'id', 'name', 'description',
        ]


class MembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    group_description = serializers.CharField(source='group.description', read_only=True)

    class Meta:
        model = Membership
        fields = [
            'id',
            'user',
            'user_email',
            'user_username',
            'group',
            'group_name',
            'group_description',
        ]


class MembershipRuleSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = MembershipRule
        fields = [
            'id',
            'name',
            'domain',
            'group',
            'group_name',
        ]


class GroupCourseSerializer(serializers.ModelSerializer):
    course = CourseKeyField(source='course_id')
    course_name = serializers.CharField(source='course.display_name_with_default', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = GroupCourse
        fields = [
            'id',
            'course',
            'course_name',
            'group',
            'group_name',
        ]
