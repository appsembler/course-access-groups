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
from rest_framework.permissions import IsAuthenticated


class CommonAuthMixin(object):
    """
    Provides a common authorization base for the Figures API views.
    """
    authentication_classes = (
        BasicAuthentication,
        SessionAuthentication,
        TokenAuthentication,
    )
    permission_classes = (
        IsAuthenticated,
        # figures.permissions.IsSiteAdminUser,
    )
