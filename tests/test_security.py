# -*- coding: utf-8 -*-
"""
Test the authentication and permission of Course Access Groups.
"""

from __future__ import absolute_import, unicode_literals

import pytest
from rest_framework.authentication import TokenAuthentication
from openedx.core.lib.api.authentication import OAuth2Authentication
from course_access_groups.permissions import (
    CommonAuthMixin,
)


class TestCommonAuthMixin(object):
    """
    Tests for CommonAuthMixin.

    This class is minimal because CommonAuthMixin should be tested in `test_api_permissions`.
    """

    @pytest.mark.parametrize('auth_backend, reason', [
        [OAuth2Authentication, 'Should work with Bearer OAuth token from within AMC'],
        [TokenAuthentication, 'Should work with API Token for external usage'],
    ])
    def test_token_authentication(self, auth_backend, reason):
        """
        Ensures that the APIs are usable with an API Token besides the AMC Bearer token.
        """
        assert auth_backend in CommonAuthMixin.authentication_classes, reason
