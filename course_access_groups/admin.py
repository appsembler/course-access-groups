# -*- coding: utf-8 -*-
"""
Admins for the Course Access Groups module.
"""

from __future__ import absolute_import, unicode_literals


from django.contrib import admin
from django.contrib.admin import TabularInline

from course_access_groups.models import (
    CourseAccessGroup,
    GroupCourse,
    Membership,
    MembershipRule,
)


class GroupCourseInline(TabularInline):
    """
    Allow adding courses to groups.
    """

    model = GroupCourse
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
