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
    PublicCourse,
)
from course_access_groups.permissions import get_current_organization


class CourseKeyFieldWithPermission(serializers.RelatedField):
    """
    Serializer field for a model CourseKey field with permission checks on the current organization.

    This inspired by the openedx.core.lib.api.serializers.
    """

    def get_queryset(self):
        organization = get_current_organization(self.context['request'])
        organization_courses = OrganizationCourse.objects.filter(organization=organization, active=True)
        return CourseOverview.objects.filter(
            id__in=organization_courses.values('course_id'),
        )

    def to_internal_value(self, data):
        """
        Convert a unicode to a course key.
        """
        validation_error = ValidationError('Invalid course key: {id}'.format(id=data))

        try:
            course_key = CourseKey.from_string(data)
        except InvalidKeyError:
            raise validation_error

        try:
            return self.get_queryset().get(id=course_key).id
        except CourseOverview.DoesNotExist:
            raise validation_error

    def to_representation(self, course_key):
        """
        Course API representation.
        """
        try:
            course = self.get_queryset().get(id=course_key)
        except CourseOverview.DoesNotExist:
            raise ValidationError('Something went wrong with your request.')

        return {
            'id': text_type(course.id),
            'name': course.display_name_with_default,
        }


class UserFieldWithPermission(serializers.RelatedField):
    """
    Serializer field for a model User foreign key with permission checks on the current organization.
    """

    def get_queryset(self):
        organization = get_current_organization(self.context['request'])
        return get_user_model().objects.filter(
            id__in=UserOrganizationMapping.objects.filter(
                organization=organization,
                is_active=True,
            ).values('user_id'),
        )

    def to_internal_value(self, user_id):
        try:
            return self.get_queryset().get(id=user_id)
        except get_user_model().DoesNotExist:
            raise ValidationError('Invalid user key: {id}'.format(id=user_id))

    def to_representation(self, user):
        return {
            'id': user.id,
            'email': user.email,
            'username': user.username,
        }


class CourseAccessGroupFieldWithPermission(serializers.RelatedField):
    """
    Serializer field for a model CourseAccessGroup foreign key with permission checks on the current organization.
    """

    def get_queryset(self):
        organization = get_current_organization(self.context['request'])
        return CourseAccessGroup.objects.filter(
            organization=organization,
        )

    def to_internal_value(self, data):
        try:
            return self.get_queryset().get(pk=data)
        except CourseAccessGroup.DoesNotExist:
            raise ValidationError('Invalid group id: {id}'.format(
                id=data,
            ))

    def to_representation(self, value):
        return {
            'id': value.pk,
            'name': value.name,
        }


class CourseAccessGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseAccessGroup
        fields = [
            'id', 'name', 'description',
        ]


class MembershipSerializer(serializers.ModelSerializer):
    user = UserFieldWithPermission()
    group = CourseAccessGroupFieldWithPermission()

    class Meta:
        model = Membership
        fields = [
            'id',
            'user',
            'group',
        ]


class MembershipRuleSerializer(serializers.ModelSerializer):
    group = CourseAccessGroupFieldWithPermission()

    class Meta:
        model = MembershipRule
        fields = [
            'id',
            'name',
            'domain',
            'group',
        ]


class PublicCourseSerializer(serializers.ModelSerializer):
    course = CourseKeyFieldWithPermission(source='course_id')

    class Meta:
        model = PublicCourse
        fields = [
            'id',
            'course',
        ]


class MembershipSubSerializer(serializers.ModelSerializer):
    group = CourseAccessGroupFieldWithPermission()

    class Meta:
        model = Membership
        fields = [
            'id',
            'group',
        ]


class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='profile.name', read_only=True)
    membership = MembershipSubSerializer(read_only=True)

    class Meta:
        model = get_user_model()
        fields = [
            'id',
            'username',
            'name',
            'email',
            'membership',
        ]


class GroupCourseSubSerializer(serializers.ModelSerializer):
    group = CourseAccessGroupFieldWithPermission()

    class Meta:
        model = GroupCourse
        fields = [
            'id',
            'group',
        ]


class CourseOverviewSerializer(serializers.ModelSerializer):
    id = serializers.CharField()
    public_status = serializers.SerializerMethodField()
    group_links = GroupCourseSubSerializer(many=True, read_only=True, source='group_courses')
    name = serializers.CharField(source='display_name_with_default')

    class Meta:
        model = CourseOverview
        fields = [
            'id',
            'name',
            'public_status',
            'group_links',
        ]

    def get_public_status(self, course):
        try:
            public_course = PublicCourse.objects.get(course_id=course.id)
            return {
                'id': public_course.id,
                'is_public': True,
            }
        except PublicCourse.DoesNotExist:
            return {
                'is_public': False,
            }


class GroupCourseSerializer(serializers.ModelSerializer):
    course = CourseKeyFieldWithPermission(source='course_id')
    group = CourseAccessGroupFieldWithPermission()

    class Meta:
        model = GroupCourse
        fields = [
            'id',
            'course',
            'group',
        ]
