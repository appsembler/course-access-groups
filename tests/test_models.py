# -*- coding: utf-8 -*-
"""
Tests for the `course-access-groups` models module.
"""


import pytest
from django.core.exceptions import ValidationError
from organizations.models import UserOrganizationMapping

from course_access_groups.models import CourseAccessGroup, Membership, MembershipRule
from course_access_groups.signals import on_learner_account_activated
from test_utils.factories import CourseAccessGroupFactory, MembershipRuleFactory, UserFactory


@pytest.mark.django_db
class TestMembershipRuleModel:
    """
    Tests for MembershipRule model.
    """

    @pytest.mark.parametrize('domain', [
        'example.com',
        'example.co.uk',
        'hello-world.org',
    ])
    def test_valid_domains(self, domain):
        rule = MembershipRuleFactory.create(domain=domain)
        rule.full_clean()
        assert rule

    @pytest.mark.parametrize('domain', [
        '@example.com',
        '111',
        '===',
        ' example.com ',  # has spaces
    ])
    def test_invalid_domains(self, domain):
        with pytest.raises(ValidationError):
            rule = MembershipRuleFactory.create(domain=domain)
            rule.full_clean()


@pytest.mark.django_db
class TestMembershipRuleApply:
    """
    Test the on_learner_account_activated signal and its MembershipRule.apply_for_user helper.
    """

    @pytest.mark.parametrize('email, should_enroll', [
        ['someone@known_site.com', True],
        ['another.one@other_site.com', False],
    ])
    def test_simple_match(self, email, should_enroll):
        """
        Basic test for membership rules.
        """
        assert not Membership.objects.count()
        user = UserFactory.create(is_active=True, email=email)
        group = CourseAccessGroupFactory.create()
        UserOrganizationMapping.objects.create(id=500, user=user, organization=group.organization)
        MembershipRule.objects.create(name='Something', domain='known_site.com', group=group)

        on_learner_account_activated(self.__class__, user)
        membership = Membership.objects.filter(user=user).first()

        assert bool(membership) == should_enroll
        assert not membership or (membership.group == group)

    def test_inactive_user(self):
        """
        Ensure inactive user don't get a rule by mistake.
        """
        user = UserFactory.create(is_active=False)
        with pytest.raises(ValueError):
            on_learner_account_activated(self.__class__, user)


class TestCourseAccessGroupModel:
    """
    Tests for the CourseAccessGroup model.
    """

    def test_str(self):
        group = CourseAccessGroup(name='hello world')
        assert str(group) == 'hello world'
        assert str(group) == 'hello world'
