# -*- coding: utf-8 -*-
"""
Tests for the CourseAccessGroupsConfig, mostly for the Open edX plugin system.
"""


from course_access_groups import apps


class TestCourseAccessGroupsConfig(object):
    """
    Testing CourseAccessGroupsConfig.
    """

    def test_plugin_config(self):
        """
        Check for syntax or other severe errors in CourseAccessGroupsConfig.plugin_app.
        """
        config = apps.CourseAccessGroupsConfig('course_access_groups', apps)
        assert type(config.plugin_app) == dict
