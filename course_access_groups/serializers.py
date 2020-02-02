# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from rest_framework import serializers
from openedx.core.lib.api.serializers import CourseKeyField
from course_access_groups.models import (
    Group,
    CourseGroup,
    Membership,
    Rule,
)


class GroupSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    organization_name = serializers.ReadOnlyField(source='organization.name')

    class Meta:
        model = Group
        fields = [
            'id', 'name', 'description', 'organization', 'organization_name',
        ]


class MembershipSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    user_email = serializers.ReadOnlyField(source='user.email')
    user_username = serializers.ReadOnlyField(source='user.username')
    group_name = serializers.ReadOnlyField(source='group.name')
    group_description = serializers.ReadOnlyField(source='group.description')

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


class RuleSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    group_name = serializers.ReadOnlyField(source='group.name')

    class Meta:
        model = Rule
        fields = [
            'id',
            'name',
            'domain',
            'group',
            'group_name',
        ]


class CourseGroupSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    course = CourseKeyField(source='course_id')
    course_name = serializers.ReadOnlyField(source='course.display_name_with_default')
    group_name = serializers.ReadOnlyField(source='group.name')

    class Meta:
        model = CourseGroup
        fields = [
            'id',
            'course',
            'course_name',
            'group',
            'group_name',
        ]
