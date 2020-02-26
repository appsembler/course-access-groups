# -*- coding: utf-8 -*-
"""
Tests for the CAG API ViewSets.
"""

from __future__ import absolute_import, unicode_literals

from course_access_groups.models import (
    CourseAccessGroup,
    GroupCourse,
    Membership,
    MembershipRule,
)
from course_access_groups.permissions import CommonAuthMixin
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
class ViewSetTestBase(object):
    """
    Base class for ViewSet test cases.
    """

    @pytest.fixture(autouse=True)
    def setup(self, settings, monkeypatch):
        settings.SITE_ID = 1  # Mock get_current_site

        # Skip permissions on API calls
        monkeypatch.setattr(CommonAuthMixin, 'authentication_classes', [])
        monkeypatch.setattr(CommonAuthMixin, 'permission_classes', [])


class TestCourseAccessGroupsViewSet(ViewSetTestBase):
    """
    Tests for the CourseAccessGroupsViewSet APIs.
    """

    url = '/course-access-groups/'

    def test_urls_sanity_check(self, client):
        """
        A basic sanity check for URLs to ensure nothing is broken.
        """
        response = client.get(self.url)
        assert response.status_code == 200

    def test_no_groups(self, client):
        response = client.get(self.url)
        results = response.json()['results']
        assert results == []

    def test_list_groups(self, client):
        CourseAccessGroupFactory.create_batch(3)
        response = client.get(self.url)
        results = response.json()['results']
        assert len(results) == 3

    def test_one_group(self, client):
        group = CourseAccessGroupFactory.create()
        response = client.get('/course-access-groups/{}/'.format(group.id))
        assert response.status_code == 200
        result = response.json()
        assert result == {
            'id': group.id,
            'name': group.name,
            'description': group.description,
            'organization': group.organization.id,
            'organization_name': group.organization.name,
        }

    def test_add_group(self, client):
        assert not CourseAccessGroup.objects.count()
        org = OrganizationFactory.create()
        response = client.post('/course-access-groups/', data={
            'name': 'Awesome Group',
            'description': 'My group',
            'organization': org.id,
        })
        assert response.status_code == 201
        new_group = CourseAccessGroup.objects.get()
        assert new_group.organization.id == org.id
        assert new_group.name == 'Awesome Group'

    def test_delete_group(self, client):
        """
        Ensure group deletion is possible via the API.
        """
        group = CourseAccessGroupFactory.create()
        response = client.delete('/course-access-groups/{}/'.format(group.id))
        assert response.status_code == 204
        assert not CourseAccessGroup.objects.count()


class TestMembershipViewSet(ViewSetTestBase):
    """
    Tests for the MembershipViewSet APIs.
    """

    url = '/memberships/'

    def test_no_memberships(self, client):
        response = client.get(self.url)
        assert response.status_code == 200
        results = response.json()['results']
        assert results == []

    def test_list_memberships(self, client):
        MembershipFactory.create_batch(3, group=CourseAccessGroupFactory.create())
        response = client.get(self.url)
        assert response.status_code == 200
        results = response.json()['results']
        assert len(results) == 3

    def test_one_membership(self, client):
        membership = MembershipFactory.create()
        response = client.get('/memberships/{}/'.format(membership.id))
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

    def test_add_membership(self, client):
        assert not Membership.objects.count()
        group = CourseAccessGroupFactory.create()
        user = UserFactory.create()
        response = client.post(self.url, {
            'group': group.id,
            'user': user.id,
        })
        assert response.status_code == 201
        new_membership = Membership.objects.get()
        assert new_membership.group.id == group.id
        assert new_membership.user.id == user.id

    def test_delete_membership(self, client):
        """
        Ensure membership deletion is possible via the API.
        """
        membership = MembershipFactory.create()
        response = client.delete('/memberships/{}/'.format(membership.id))
        assert response.status_code == 204
        assert not Membership.objects.count()


class TestMembershipRuleViewSet(ViewSetTestBase):
    """
    Tests for the MembershipRuleViewSet APIs.
    """

    url = '/membership-rules/'

    def test_no_rules(self, client):
        response = client.get(self.url)
        assert response.status_code == 200
        results = response.json()['results']
        assert results == []

    def test_list_rules(self, client):
        MembershipRuleFactory.create_batch(3, group=CourseAccessGroupFactory.create())
        response = client.get(self.url)
        assert response.status_code == 200
        results = response.json()['results']
        assert len(results) == 3

    def test_one_rule(self, client):
        rule = MembershipRuleFactory.create()
        response = client.get('/membership-rules/{}/'.format(rule.id))
        result = response.json()
        assert result == {
            'id': rule.id,
            'name': rule.name,
            'domain': rule.domain,
            'group': rule.group.id,
            'group_name': rule.group.name,
        }

    def test_add_rule(self, client):
        assert not MembershipRule.objects.count()
        group = CourseAccessGroupFactory.create()
        domain = 'example.org'
        response = client.post(self.url, {
            'group': group.id,
            'name': 'Community assignment',
            'domain': domain,
        })
        assert response.status_code == 201
        new_rule = MembershipRule.objects.get()
        assert new_rule.group.id == group.id
        assert new_rule.domain == domain
        assert new_rule.name == 'Community assignment'

    def test_delete_rule(self, client):
        """
        Ensure rule deletion is possible via the API.
        """
        rule = MembershipRuleFactory.create()
        response = client.delete('/membership-rules/{}/'.format(rule.id))
        assert response.status_code == 204
        assert not MembershipRule.objects.count()


class TestGroupCourseViewSet(ViewSetTestBase):
    """
    Tests for the GroupCourseViewSet APIs.
    """

    url = '/group-courses/'

    def test_no_links(self, client):
        response = client.get(self.url)
        assert response.status_code == 200
        results = response.json()['results']
        assert results == []

    def test_list_links(self, client):
        GroupCourseFactory.create_batch(3, group=CourseAccessGroupFactory.create())
        response = client.get(self.url)
        assert response.status_code == 200
        results = response.json()['results']
        assert len(results) == 3

    def test_one_link(self, client):
        link = GroupCourseFactory.create()
        response = client.get('/group-courses/{}/'.format(link.id))
        result = response.json()
        assert result == {
            'id': link.id,
            'course': str(link.course.id),
            'course_name': link.course.display_name_with_default,
            'group': link.group.id,
            'group_name': link.group.name,
        }

    def test_add_link(self, client):
        assert not GroupCourse.objects.count()
        group = CourseAccessGroupFactory.create()
        course = CourseOverviewFactory.create()
        response = client.post(self.url, {
            'group': group.id,
            'course': str(course.id),
        })
        assert response.status_code == 201
        new_link = GroupCourse.objects.get()
        assert new_link.group.id == group.id
        assert new_link.course.id == course.id

    def test_delete_link(self, client):
        """
        Ensure link deletion is possible via the API.
        """
        link = GroupCourseFactory.create()
        response = client.delete('/group-courses/{}/'.format(link.id))
        assert response.status_code == 204
        assert not GroupCourse.objects.count()
