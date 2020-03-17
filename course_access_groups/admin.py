# -*- coding: utf-8 -*-
"""
Admins for the Course Access Groups module.
"""

from __future__ import absolute_import, unicode_literals

from six import text_type
from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError
from django import forms
from django.core.exceptions import ValidationError
from django.contrib import admin
from django.contrib.admin import TabularInline

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

from course_access_groups.models import (
    CourseAccessGroup,
    GroupCourse,
    Membership,
    MembershipRule,
    PublicCourse,
)


class CourseKeyFormMixin(object):
    """
    A form mixin to make it easy to enter course keys in admin.
    """

    def clean_course(self):
        course = self.cleaned_data['course']
        if course and not isinstance(course, CourseKey):
            try:
                course = CourseKey.from_string(course)
            except InvalidKeyError as e:
                raise ValidationError('Invalid Key Error: {}'.format(e.message))

        if course:
            try:
                return CourseOverview.objects.get(pk=course)
            except CourseOverview.DoesNotExist:
                raise ValidationError('Course not found: {}'.format(course))


class GroupCourseInlineForm(CourseKeyFormMixin, forms.ModelForm):
    course = forms.CharField()

    class Meta:
        fields = ['course']
        model = GroupCourse


class GroupCourseInline(TabularInline):
    """
    Allow adding courses to groups.
    """

    model = GroupCourse
    form = GroupCourseInlineForm
    extra = 2


@admin.register(CourseAccessGroup)
class CourseAccessGroupAdmin(admin.ModelAdmin):
    """
    Admin for CourseAccessGroup model.
    """

    list_display = [
        'id',
        'name',
        'description',
        'organization_id',
        'organization',
    ]

    list_display_links = list_display[:2]

    search_fields = [
        'name',
        'description',
        'organization__name',
    ]

    list_filter = [
        'organization',
    ]

    ordering = ['-created']

    inlines = [
        GroupCourseInline,
    ]

    def get_readonly_fields(self, request, obj=None):
        """
        Changing the organization isn't a good idea.
        """
        if obj:
            return ['organization']

        return []


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    """
    Admin for Membership model.
    """

    list_display = [
        'id',
        'user_username',
        'user_email',
        'group',
        'group_organization',
        'automatic',
    ]

    list_display_links = list_display[:3]

    search_fields = [
        'user__email',
        'user__username',
        'group__name',
        'group__organization__name',
    ]

    list_filter = [
        'group',
        'group__organization',
        'automatic',
    ]

    ordering = ['-created']

    def user_username(self, object):
        """
        Get the username.
        """
        return object.user.username

    def user_email(self, object):
        """
        Get the user email.
        """
        return object.user.email

    def group_organization(self, membership):
        """
        Get the organization name.
        """
        return membership.group.organization.name


@admin.register(MembershipRule)
class MembershipRuleAdmin(admin.ModelAdmin):
    """
    Admin for MembershipRule model.
    """

    list_display = [
        'id',
        'name',
        'domain',
        'group',
        'group_organization',
    ]

    list_display_links = list_display[:2]

    search_fields = [
        'name',
        'group__name',
        'group__organization__name',
    ]

    list_filter = [
        'group',
        'group__organization',
    ]

    ordering = ['-created']

    def group_organization(self, rule):
        """
        Get the organization name.
        """
        return rule.group.organization.name


class PublicCourseForm(CourseKeyFormMixin, forms.ModelForm):
    course = forms.CharField()

    class Meta:
        model = PublicCourse
        fields = ['course']


@admin.register(PublicCourse)
class PublicCourseAdmin(admin.ModelAdmin):
    """
    Admin for PublicCourse model.
    """

    list_display = [
        'course_name',
        'course_id',
    ]

    list_display_links = list_display

    search_fields = [
        'course__display_name',
    ]

    ordering = ['-created']
    form = PublicCourseForm

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['course']

        return []

    def course_id(self, public_course):
        """
        Get the course id.
        """
        return text_type(public_course.course.id)

    def course_name(self, public_course):
        """
        Get the course name.
        """
        return public_course.course.display_name_with_default
