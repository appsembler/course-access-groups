# -*- coding: utf-8 -*-
"""
Test the authentication and permission of Course Access Groups.
"""

from __future__ import absolute_import, unicode_literals

import pytest
from django.contrib.auth import get_user_model
from course_access_groups.permissions import (
    is_active_staff_or_superuser,
)


@pytest.mark.django_db
class TestStaffSuperuserHelper(object):
    """
    Tests for permissions.is_active_staff_or_superuser.
    """

    def test_none_user(self):
        assert not is_active_staff_or_superuser(None)

    @pytest.mark.parametrize('username, allow', [
        ('regular_user', False),
        ('staff_user', True),
        ('super_user', True),
        ('superstaff_user', True),
    ])
    def test_active_user(self, standard_test_users, username, allow):  # pylint: disable=unused-argument
        user = get_user_model().objects.get(username=username)
        assert is_active_staff_or_superuser(user) == allow

    @pytest.mark.parametrize('username', [
        'regular_user',
        'staff_user',
        'super_user',
        'superstaff_user',
    ])
    def test_inactive_user(self, standard_test_users, username):  # pylint: disable=unused-argument
        user = get_user_model().objects.get(username=username)
        user.is_active = False
        assert not is_active_staff_or_superuser(user)
