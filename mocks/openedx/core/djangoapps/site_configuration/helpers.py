"""
Mock Site Configuration Helpers.

Use `test_utils.patch_site_configs` to patch the site configuration.
"""

MOCK_SITE_CONFIG_VALUES = {
    'ENABLE_COURSE_ACCESS_GROUPS': True,
}


def get_value(val_name, default=None, **kwargs):  # pylint: disable=unused-argument
    """
    Mock openedx.core.djangoapps.site_configuration.helpers.get_value.
    """
    return MOCK_SITE_CONFIG_VALUES.get(val_name, default)
