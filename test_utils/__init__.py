"""
Test utilities.

Since pytest discourages putting __init__.py into test directory (i.e. making tests a package)
one cannot import from anywhere under tests folder. However, some utility classes/methods might be useful
in multiple test modules (i.e. factoryboy factories, base test classes). So this package is the place to put them.
"""


from mock import patch

from django.views import View
import course_access_groups.views


def patch_site_configs(values):
    """
    Helper to mock site configuration values.

    :param values dict.

    Use either as `@patch_site_configs(...)` or `with patch_site_configs(...):`.
    """
    return patch.dict('openedx.core.djangoapps.site_configuration.helpers.MOCK_SITE_CONFIG_VALUES', values)


def get_api_view_classes():
    """
    Auto-discover all API View (ViewSets or otherwise) in Course Access Group.

    This list is used for security checks.
    """
    api_view_classes = []
    for var_name in dir(course_access_groups.views):
        api_view_class = getattr(course_access_groups.views, var_name)

        # Filtering for all Django Views.
        if isinstance(api_view_class, type) and issubclass(api_view_class, View):
            api_view_classes.append(api_view_class)

    return api_view_classes
