# -*- coding: utf-8 -*-
"""
Access Control backends to implement the Course Access Groups.
"""

from __future__ import absolute_import, unicode_literals


from courseware.access_utils import (
    ACCESS_DENIED,
    ACCESS_GRANTED,
)
from course_access_groups.feature_flag import is_feature_enabled
from course_access_groups.permissions import user_has_access_to_course


def user_has_access(user, resource, default_has_access, options):  # pylint: disable=unused-argument
    """
    The Access Control Backend to plug the Course Access Groups feature in Open edX.

    :param user: User to check access against.
    :param resource: Usually a Course or CourseOverview object to check access for.
    :param default_has_access: The platform default access check, useful as a callback.
    :param options: Extra options, nothing in particular here.
    :return: bool: whether the user is granted access or no.
    """
    if not is_feature_enabled():
        # Plugin is turned off, maintain the platform's default behaviour.
        return default_has_access

    if not default_has_access:
        # Only permit resources that both Open edX [and] CAG rules allow.
        # i.e. Course Access Groups should not leak resources that Open edX don't want to permit.
        # e.g. In case the `course.is_deleted` feature is enabled, Open edX would prevent course access regardless
        # of the permission. It's good to have the CAG module future proof in case of such changes.
        return default_has_access

    if user_has_access_to_course(user, resource):
        return ACCESS_GRANTED
    else:
        return ACCESS_DENIED


__all__ = ['user_has_access']
