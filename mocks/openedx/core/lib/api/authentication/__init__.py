"""
Mocks for openedx.core.lib.api.authentication.
"""

from rest_framework.authentication import BaseAuthentication


class OAuth2Authentication(BaseAuthentication):
    """
    Creating temperary class cause things outside of edx-platform need OAuth2Authentication.
    This will be removed when repos outside edx-platform import BearerAuthentiction instead.

    Note (Omar): Could be removed in the Koa release. Nothing to do for now, but if it breaks, we need
                 to switch to BearerAuthentiction.
    """

    def authenticate(self, request):
        """
        Fake authentication method that doesn't authenticate.
        """
        return
