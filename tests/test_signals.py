"""
Tests for signal handlers.
"""


import pytest

from course_access_groups.models import Membership
from course_access_groups.signals import (
    on_learner_account_activated,
    on_learner_register,
)

from test_utils.factories import (
    MembershipRuleFactory,
    UserFactory,
    UserOrganizationMappingFactory,
)


@pytest.mark.django_db
@pytest.mark.parametrize('receiver_function', [
    on_learner_account_activated,
    on_learner_register,
])
def test_working_on_account_activated_signal(receiver_function):
    """
    Ensure USER_ACCOUNT_ACTIVATED and REGISTER_USER signals are processed correctly.
    """
    rule = MembershipRuleFactory(domain='example.com')
    mapping = UserOrganizationMappingFactory.create(
        user__email='someone@example.com',
        organization=rule.group.organization,
    )

    receiver_function(object(), mapping.user)
    assert Membership.objects.filter(user=mapping.user).exists(), 'Should create the rule'

    receiver_function(object(), mapping.user)  # Should not fail when receiving the signal twice


@pytest.mark.django_db
@pytest.mark.parametrize('receiver_function,signal_name', [
    [on_learner_account_activated, 'USER_ACCOUNT_ACTIVATED'],
    [on_learner_register, 'REGISTER_USER'],
])
def test_failed_on_account_activated_signal(monkeypatch, caplog, receiver_function, signal_name):
    """
    Ensure  errors in USER_ACCOUNT_ACTIVATED and REGISTER_USER are logged.
    """
    monkeypatch.delattr(Membership, 'create_from_rules')  # Act as if create_from_rules() don't work!

    user = UserFactory.create(email='someone@example.com')
    MembershipRuleFactory(domain='example.com')

    with pytest.raises(AttributeError):
        receiver_function(object(), user)
    assert 'Error receiving {signal_name} signal for user'.format(signal_name=signal_name) in caplog.text
    assert 'someone@example.com' in caplog.text
    assert 'AttributeError' in caplog.text
