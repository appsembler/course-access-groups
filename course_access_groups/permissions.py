# -*- coding: utf-8 -*-
"""
Course Access Groups permission and authentication classes.
"""

from __future__ import absolute_import, unicode_literals

from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
    TokenAuthentication,
)
from openedx.core.lib.api.authentication import OAuth2Authentication
from rest_framework.permissions import IsAuthenticated


class CommonAuthMixin(object):
    """
    Provides a common authorization base for the Course Access Groups API views.
    """

    authentication_classes = (
        BasicAuthentication,
        SessionAuthentication,
        TokenAuthentication,
        OAuth2Authentication,
    )
    permission_classes = (
        IsAuthenticated,
        # TODO: Add IsSiteAdminUser,
    )


def is_active_staff_or_superuser(user):
    """
    Checks if user is active staff or superuser.
    """
    return user and user.is_active and (user.is_staff or user.is_superuser)