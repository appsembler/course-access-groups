# -*- coding: utf-8 -*-
"""
Tests for the CAG API ViewSets.
"""

from __future__ import absolute_import, unicode_literals

from six import text_type
import pytest

from organizations.models import Organization, OrganizationCourse, UserOrganizationMapping
from course_access_groups.models import (
    CourseAccessGroup,
    GroupCourse,
    Membership,
    MembershipRule,
)
from test_utils.factories import (
    CourseOverviewFactory,
    MembershipFactory,
    MembershipRuleFactory,
    GroupCourseFactory,
)
from test_utils.factories import (
    UserFactory,
    CourseAccessGroupFactory,
    OrganizationFactory,
    SiteFactory,
)


@pytest.mark.django_db
class ViewSetTestBase(object):
    """
    Base class for ViewSet test cases.
    """

    domain = 'mydomain.com'

    @pytest.fixture(autouse=True)
    def setup(self, client):
        # pylint: disable=attribute-defined-outside-init
        client.defaults['SERVER_NAME'] = self.domain
        self.user = UserFactory.create(username='org_staff')
        self.site = SiteFactory.create(domain=self.domain)
        self.my_org = OrganizationFactory.create(name='my_org', sites=[self.site])
        self.other_org = OrganizationFactory.create(name='other_org')
        self.staff = UserOrganizationMapping.objects.create(
            user=self.user,
            organization=self.my_org,
            is_amc_admin=True,
        )
        client.force_login(self.user)


class TestCourseAccessGroupsViewSet(ViewSetTestBase):
    """
    Tests for the CourseAccessGroupsViewSet APIs.
    """

    url = '/course-access-groups/'

    def test_sanity_check(self, client):
        assert self.user.is_active
        assert list(self.my_org.sites.all()) == [self.site], 'There should be one organization site.'
        response = client.get(self.url)
        assert response.json()['results'] == []

    @pytest.mark.parametrize('org_name, status_code, expected_count', [
        ['my_org', 200, 3],
        ['other_org', 200, 0],
    ])
    def test_list_groups(self, client, org_name, status_code, expected_count):
        org = Organization.objects.get(name=org_name)
        CourseAccessGroupFactory.create_batch(3, organization=org)
        response = client.get(self.url)
        assert response.status_code == status_code, response.content
        assert response.json()['count'] == expected_count

    @pytest.mark.parametrize('org_name, status_code, skip_response_check', [
        ['my_org', 200, False],
        ['other_org', 404, True],
    ])
    def test_one_group(self, client, org_name, status_code, skip_response_check):
        org = Organization.objects.get(name=org_name)
        group = CourseAccessGroupFactory.create(organization=org)
        response = client.get('/course-access-groups/{}/'.format(group.id))
        results = response.json()
        assert response.status_code == status_code, response.content
        assert skip_response_check or (results == {
            'id': group.id,
            'name': group.name,
            'description': group.description,
        }), 'Verify the serializer results.'

    def test_add_group(self, client):
        assert not CourseAccessGroup.objects.count()
        response = client.post(self.url, {
            'name': 'Awesome Group',
            'description': 'My group',
        })
        assert response.status_code == 201, response.content
        new_group = CourseAccessGroup.objects.get()
        assert new_group.name == 'Awesome Group'

    @pytest.mark.parametrize('org_name, status_code, expected_post_delete_count', [
        ['my_org', 204, 0],
        ['other_org', 404, 1],
    ])
    def test_delete_group(self, client, org_name, status_code, expected_post_delete_count):
        org = Organization.objects.get(name=org_name)
        group = CourseAccessGroupFactory.create(organization=org)
        response = client.delete('/course-access-groups/{}/'.format(group.id))
        assert response.status_code == status_code, response.content
        assert CourseAccessGroup.objects.count() == expected_post_delete_count


@pytest.mark.skip('Broken for now, will re-enable soon.')
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


@pytest.mark.skip('Broken for now, will re-enable soon.')
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


@pytest.mark.skip('Broken for now, will re-enable soon.')
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
