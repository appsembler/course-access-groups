# -*- coding: utf-8 -*-
"""
Signals and receivers for Course Access Groups.
"""


from .models import Membership


def on_learner_account_activated(sender, user, **kwargs):
    """
    Receive the `USER_ACCOUNT_ACTIVATED` signal to apply MembershipRule.

    :param sender: The sender class.
    :param user: The activated learner.
    :param kwargs: Extra keyword args.
    """
    Membership.create_from_rules(user)
