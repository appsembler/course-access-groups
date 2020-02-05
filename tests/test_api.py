# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import unittest
from django.test import Client
from course_access_groups.models import (
    CourseAccessGroup,
    GroupCourse,
    Membership,
    MembershipRule,
)
import pytest
from test_utils.factories import (
    UserFactory,
    CourseAccessGroupFactory,
    CourseOverviewFactory,
    MembershipFactory,
    OrganizationFactory,
    MembershipRuleFactory,
    GroupCourseFactory,
)


@pytest.mark.django_db
class CourseAccessGroupsViewTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.url = '/course-access-groups/'

    def test_urls(self):
        response = self.client.get(self.url)
        assert response.status_code == 200

    def test_no_groups(self):
        response = self.client.get(self.url)
        results = response.json()['results']
        assert results == []

    def test_list_groups(self):
        CourseAccessGroupFactory.create_batch(3)
        response = self.client.get(self.url)
        results = response.json()['results']
        assert len(results) == 3

    def test_one_group(self):
        group = CourseAccessGroupFactory.create()
        response = self.client.get('/course-access-groups/{}/'.format(group.id))
        assert response.status_code == 200
        result = response.json()
        assert result == {
            'id': group.id,
            'name': group.name,
            'description': group.description,
            'organization': group.organization.id,
            'organization_name': group.organization.name,
        }

    def test_add_group(self):
        assert not CourseAccessGroup.objects.count()
        org = OrganizationFactory.create()
        response = self.client.post('/course-access-groups/', data={
            'name': 'Awesome Group',
            'description': 'My group',
            'organization': org.id,
        })
        assert response.status_code == 201
        new_group = CourseAccessGroup.objects.get()
        assert new_group.organization.id == org.id
        assert new_group.name == 'Awesome Group'


@pytest.mark.django_db
class MembershipViewTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.url = '/memberships/'

    def test_no_memberships(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        results = response.json()['results']
        assert results == []

    def test_list_memberships(self):
        MembershipFactory.create_batch(3, group=CourseAccessGroupFactory.create())
        response = self.client.get(self.url)
        assert response.status_code == 200
        results = response.json()['results']
        assert len(results) == 3

    def test_one_membership(self):
        membership = MembershipFactory.create()
        response = self.client.get('/memberships/{}/'.format(membership.id))
        result = response.json()
        assert result == {
            'id': membership.id,
            'user': membership.user.id,
            'user_email': membership.user.email,
            'user_username': membership.user.username,
            'group': membership.group.id,
            'group_name': membership.group.name,
            'group_description': membership.group.description,
        }

    def test_add_membership(self):
        assert not Membership.objects.count()
        group = CourseAccessGroupFactory.create()
        user = UserFactory.create()
        response = self.client.post(self.url, {
            'group': group.id,
            'user': user.id,
        })
        assert response.status_code == 201
        new_membership = Membership.objects.get()
        assert new_membership.group.id == group.id
        assert new_membership.user.id == user.id


@pytest.mark.django_db
class MembershipRuleViewTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.url = '/membership-rules/'

    def test_no_rules(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        results = response.json()['results']
        assert results == []

    def test_list_rules(self):
        MembershipRuleFactory.create_batch(3, group=CourseAccessGroupFactory.create())
        response = self.client.get(self.url)
        assert response.status_code == 200
        results = response.json()['results']
        assert len(results) == 3

    def test_one_rule(self):
        rule = MembershipRuleFactory.create()
        response = self.client.get('/membership-rules/{}/'.format(rule.id))
        result = response.json()
        assert result == {
            'id': rule.id,
            'name': rule.name,
            'domain': rule.domain,
            'group': rule.group.id,
            'group_name': rule.group.name,
        }

    def test_add_rule(self):
        assert not MembershipRule.objects.count()
        group = CourseAccessGroupFactory.create()
        domain = 'example.org'
        response = self.client.post(self.url, {
            'group': group.id,
            'name': 'Community assignment',
            'domain': domain,
        })
        assert response.status_code == 201
        new_rule = MembershipRule.objects.get()
        assert new_rule.group.id == group.id
        assert new_rule.domain == domain
        assert new_rule.name == 'Community assignment'


@pytest.mark.django_db
class GroupCourseViewTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.url = '/group-courses/'

    def test_no_links(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        results = response.json()['results']
        assert results == []

    def test_list_links(self):
        GroupCourseFactory.create_batch(3, group=CourseAccessGroupFactory.create())
        response = self.client.get(self.url)
        assert response.status_code == 200
        results = response.json()['results']
        assert len(results) == 3

    def test_one_link(self):
        link = GroupCourseFactory.create()
        response = self.client.get('/group-courses/{}/'.format(link.id))
        result = response.json()
        assert result == {
            'id': link.id,
            'course': str(link.course.id),
            'course_name': link.course.display_name_with_default,
            'group': link.group.id,
            'group_name': link.group.name,
        }

    def test_add_link(self):
        assert not GroupCourse.objects.count()
        group = CourseAccessGroupFactory.create()
        course = CourseOverviewFactory.create()
        response = self.client.post(self.url, {
            'group': group.id,
            'course': str(course.id),
        })
        assert response.status_code == 201
        new_link = GroupCourse.objects.get()
        assert new_link.group.id == group.id
        assert new_link.course.id == course.id
