# -*- coding: utf-8 -*-
"""
Signals and receivers for Course Access Groups.
"""

import logging

from .models import Membership

log = logging.getLogger(__name__)


def on_learner_account_activated(sender, user, **kwargs):
    """
    Receive the `USER_ACCOUNT_ACTIVATED` signal to apply MembershipRule.

    :param sender: The sender class.
    :param user: The activated learner.
    :param kwargs: Extra keyword args.
    """
    try:
        Membership.create_from_rules(user)
    except Exception:
        log.exception('Error receiving USER_ACCOUNT_ACTIVATED signal for user %s pk=%s, is_active=%s, sender=%s',
                      user.email, user.pk, user.is_active, sender)
        raise


def on_learner_register(sender, user, **kwargs):
    """
    Receive the `REGISTER_USER` signal to apply MembershipRule.

    :param sender: The sender class.
    :param user: The activated learner.
    :param kwargs: Extra keyword args.
    """
    try:
        Membership.create_from_rules(user)
    except Exception:
        log.exception('Error receiving REGISTER_USER signal for user %s pk=%s, is_active=%s, sender=%s',
                      user.email, user.pk, user.is_active, sender)
        raise
