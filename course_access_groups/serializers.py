# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from rest_framework import serializers
from openedx.core.lib.api.serializers import CourseKeyField
from course_access_groups.models import (
    CourseAccessGroup,
    GroupCourse,
    Membership,
    MembershipRule,
)


class CourseAccessGroupSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = CourseAccessGroup
        fields = [
            'id', 'name', 'description', 'organization', 'organization_name',
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
