# -*- coding: utf-8 -*-
"""
Signals and receivers for Course Access Groups.
"""

from __future__ import absolute_import, unicode_literals

from course_access_groups.models import Membership


def on_learner_account_activated(sender, user, **kwargs):  # pylint: disable=unused-argument
    """
    Receive the `USER_ACCOUNT_ACTIVATED` signal to apply MembershipRule.

    :param sender: The sender class.
    :param user: The activated learner.
    :param kwargs: Extra keyword args.
    """
    Membership.create_from_rules(user)
