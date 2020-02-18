"""
Test utilities.

Since pytest discourages putting __init__.py into test directory (i.e. making tests a package)
one cannot import from anywhere under tests folder. However, some utility classes/methods might be useful
in multiple test modules (i.e. factoryboy factories, base test classes). So this package is the place to put them.
"""
from mock import patch

from test_utils.factories import UserFactory


def patch_site_configs(values):
    """
    Helper to mock site configuration values.

    :param values dict.

    Use either as `@patch_site_configs(...)` or `with patch_site_configs(...):`.
    """
    return patch.dict('openedx.core.djangoapps.site_configuration.helpers.MOCK_SITE_CONFIG_VALUES', values)


def skip_authentication():
    """
    Helper to skip authentications on API calls.

    Use either as `@skip_authentication(...)` or `with skip_authentication(...):`.
    """
    return patch('course_access_groups.security.CommonAuthMixin.authentication_classes', [])


def skip_permission():
    """
    Helper to skip security permissions on API calls.

    Use either as `@skip_permission(...)` or `with skip_permission(...):`.
    """
    return patch('course_access_groups.security.CommonAuthMixin.permission_classes', [])


def create_standard_test_users():
    """
    Creates four test users to test the combination of permissions.

        * regular_user (is_staff=False, is_superuser=False)
        * staff_user (is_staf=True, is_superuser=False)
        * super_user (is_staff=False, is_superuser=True)
        * superstaff_user (is_staff=True, is_superuser=True)
    """
    return [
        UserFactory.create(username='regular_user'),
        UserFactory.create(username='staff_user', is_staff=True),
        UserFactory.create(username='super_user', is_superuser=True),
        UserFactory.create(username='superstaff_user', is_staff=True, is_superuser=True)
    ]
