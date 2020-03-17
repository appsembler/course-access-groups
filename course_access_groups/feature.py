"""
Feature helpers.
"""

from __future__ import absolute_import, unicode_literals

from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers


def is_feature_enabled():
    """
    Helper to check Site Configuration for ENABLE_COURSE_ACCESS_GROUPS.

    :return: bool
    """
    return bool(configuration_helpers.get_value('ENABLE_COURSE_ACCESS_GROUPS', default=False))
