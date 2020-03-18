"""
Feature helpers.
"""

from __future__ import absolute_import, unicode_literals

from django.conf import settings

from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers


class ConfigurationError(Exception):
    """
    Course Access Groups cannot run due to configuration error.
    """
    pass


def is_feature_enabled():
    """
    Helper to check Site Configuration for ENABLE_COURSE_ACCESS_GROUPS.

    :return: bool
    """
    is_enabled = bool(configuration_helpers.get_value('ENABLE_COURSE_ACCESS_GROUPS', default=False))

    if is_enabled:
        # Keep the line below in sync with `util.organizations_helpers.organizations_enabled`
        if not settings.FEATURES.get('ORGANIZATIONS_APP', False):
            raise ConfigurationError(
                'The Course Access Groups feature is enabled but the Oragnizations App is not. '
                'Please enable the feature flag `ORGANIZATIONS_APP` to fix this exception.'
            )

    return is_enabled
