# -*- coding: utf-8 -*-
"""
Course Access Groups Django application initialization.
"""

from django.apps import AppConfig
from openedx.core.djangoapps.plugins.constants import PluginSignals, PluginURLs, ProjectType


class CourseAccessGroupsConfig(AppConfig):
    """
    Configuration for the course_access_groups Django application.
    """

    name = 'course_access_groups'

    # Configuration for Open edX plugins
    plugin_app = {
        PluginURLs.CONFIG: {
            ProjectType.LMS: {
                PluginURLs.NAMESPACE: 'course_access_groups',
                PluginURLs.REGEX: '^course_access_groups/api/v1/',
            },
        },
        PluginSignals.CONFIG: {
            ProjectType.LMS: {
                PluginSignals.RECEIVERS: [
                    {
                        PluginSignals.RECEIVER_FUNC_NAME: 'on_learner_account_activated',
                        PluginSignals.SIGNAL_PATH: 'openedx.core.djangoapps.signals.signals.USER_ACCOUNT_ACTIVATED',
                    },
                    {
                        PluginSignals.RECEIVER_FUNC_NAME: 'on_learner_register',
                        PluginSignals.SIGNAL_PATH: 'openedx.core.djangoapps.user_authn.views.register.REGISTER_USER',
                    },
                ],
            }
        },
    }
