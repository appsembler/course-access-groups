"""
CAG unit test configuration and fixtures.
"""


import pytest
from test_utils.factories import UserFactory


@pytest.mark.django_db
@pytest.fixture(scope='function')
def standard_test_users():
    """
    Fixture of four test users to test the combination of permissions.

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
