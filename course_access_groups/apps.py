# -*- coding: utf-8 -*-
"""
Course Access Groups Django application initialization.
"""

from __future__ import absolute_import, unicode_literals

from django.apps import AppConfig


class CourseAccessGroupsConfig(AppConfig):
    """
    Configuration for the course_access_groups Django application.
    """

    name = 'course_access_groups'

    plugin_app = {}  # Add this app to the Open edX plugin system

    def ready(self):
        """
        Add a course field for the Course Access Groups.
        """
        from course_access_groups.monkeypatch import add_to_course_fields
        add_to_course_fields()
