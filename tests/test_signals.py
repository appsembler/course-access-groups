"""
Tests for signal handlers.
"""


import pytest

from course_access_groups.models import Membership
from course_access_groups.signals import on_learner_account_activated

from test_utils.factories import (
    MembershipRuleFactory,
    UserFactory,
    UserOrganizationMappingFactory,
)


@pytest.mark.django_db
def test_working_on_account_activated_signal():
    """
    Ensure USER_ACCOUNT_ACTIVATED is processed correctly.
    """
    rule = MembershipRuleFactory(domain='example.com')
    mapping = UserOrganizationMappingFactory.create(
        user__email='someone@example.com',
        organization=rule.group.organization,
    )

    on_learner_account_activated(object(), mapping.user)
    assert Membership.objects.filter(user=mapping.user).exists(), 'Should create the rule'


@pytest.mark.django_db
def test_failed_on_account_activated_signal(monkeypatch, caplog):
    """
    Ensure USER_ACCOUNT_ACTIVATED errors are logged.
    """
    monkeypatch.delattr(Membership, 'create_from_rules')  # Act as if the create from rules don't work!

    user = UserFactory.create(email='someone@example.com')
    MembershipRuleFactory(domain='example.com')

    with pytest.raises(AttributeError):
        on_learner_account_activated(object(), user)
    assert 'Error receiving USER_ACCOUNT_ACTIVATED signal for user' in caplog.text
    assert 'someone@example.com' in caplog.text
    assert 'AttributeError' in caplog.text
