# -*- coding: utf-8 -*-
"""
Tests for the CAG API ViewSets.
"""

from __future__ import absolute_import, unicode_literals

import json
from six import text_type
import pytest

from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
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
        ['my_org', HTTP_200_OK, 3],
        ['other_org', HTTP_200_OK, 0],
    ])
    def test_list_groups(self, client, org_name, status_code, expected_count):
        org = Organization.objects.get(name=org_name)
        CourseAccessGroupFactory.create_batch(3, organization=org)
        response = client.get(self.url)
        assert response.status_code == status_code, response.content
        assert response.json()['count'] == expected_count

    @pytest.mark.parametrize('org_name, status_code, skip_response_check', [
        ['my_org', HTTP_200_OK, False],
        ['other_org', HTTP_404_NOT_FOUND, True],
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
        assert response.status_code == HTTP_201_CREATED, response.content
        new_group = CourseAccessGroup.objects.get()
        assert new_group.name == 'Awesome Group'

    @pytest.mark.parametrize('org_name, status_code, skip_response_check', [
        ['my_org', HTTP_200_OK, False],
        ['other_org', HTTP_404_NOT_FOUND, True],
    ])
    def test_edit_group(self, client, org_name, status_code, skip_response_check):
        org = Organization.objects.get(name=org_name)
        group_before = CourseAccessGroupFactory.create(organization=org)
        url = '/course-access-groups/{}/'.format(group_before.id)
        response = client.patch(url, content_type='application/json', data=json.dumps({
            'name': 'Awesome Group',
        }))
        assert response.status_code == status_code, response.content

        if not skip_response_check:
            group_after = CourseAccessGroup.objects.get()
            assert group_after.name == 'Awesome Group'

    @pytest.mark.parametrize('org_name, status_code, expected_post_delete_count', [
        ['my_org', HTTP_204_NO_CONTENT, 0],
        ['other_org', HTTP_404_NOT_FOUND, 1],
    ])
    def test_delete_group(self, client, org_name, status_code, expected_post_delete_count):
        org = Organization.objects.get(name=org_name)
        group = CourseAccessGroupFactory.create(organization=org)
        response = client.delete('/course-access-groups/{}/'.format(group.id))
        assert response.status_code == status_code, response.content
        assert CourseAccessGroup.objects.count() == expected_post_delete_count


class TestMembershipViewSet(ViewSetTestBase):
    """
    Tests for the MembershipViewSet APIs.
    """

    url = '/memberships/'

    def test_no_memberships(self, client):
        response = client.get(self.url)
        assert response.status_code == HTTP_200_OK
        results = response.json()['results']
        assert results == []

    @pytest.mark.parametrize('org_name, expected_count', [
        ['my_org', 3],
        ['other_org', 0],
    ])
    def test_list_memberships(self, client, org_name, expected_count):
        org = Organization.objects.get(name=org_name)
        MembershipFactory.create_batch(3, group__organization=org)
        response = client.get(self.url)
        results = response.json()['results']
        assert response.status_code == HTTP_200_OK, response.content
        assert len(results) == expected_count

    @pytest.mark.parametrize('group_org, status_code, skip_response_check', [
        ['my_org', HTTP_200_OK, False],
        ['other_org', HTTP_404_NOT_FOUND, True],
    ])
    def test_one_membership(self, client, group_org, status_code, skip_response_check):
        org = Organization.objects.get(name=group_org)
        membership = MembershipFactory.create(group__organization=org)
        response = client.get('/memberships/{}/'.format(membership.id))
        assert response.status_code == status_code, response.content
        result = response.json()
        assert skip_response_check or (result == {
            'id': membership.id,
            'user': {
                'id': membership.user.id,
                'email': membership.user.email,
                'username': membership.user.username,
            },
            'group': {
                'id': membership.group.id,
                'name': membership.group.name,
            },
        }), 'Verify the serializer results.'

    @pytest.mark.parametrize('group_org, user_org, status_code, expected_count, check_new_membership', [
        ['my_org', 'my_org', HTTP_201_CREATED, 1, True],  # Should work for own users and groups
        ['my_org', 'other_org', HTTP_400_BAD_REQUEST, 0, False],  # Should not work other org's users
        ['other_org', 'my_org', HTTP_400_BAD_REQUEST, 0, False],  # Should not work for other org's groups
    ])
    def test_add_membership(self, client, group_org, user_org, status_code, expected_count, check_new_membership):
        assert not Membership.objects.count()
        group = CourseAccessGroupFactory.create(
            organization=Organization.objects.get(name=group_org),
        )
        user = UserFactory.create()
        UserOrganizationMapping.objects.create(
            organization=Organization.objects.get(name=user_org),
            user=user,
        )
        response = client.post(self.url, {
            'group': group.id,
            'user': user.id,
        })
        assert response.status_code == status_code, response.content
        assert Membership.objects.count() == expected_count
        if check_new_membership:
            new_membership = Membership.objects.get()
            assert new_membership.group.id == group.id
            assert new_membership.user.id == user.id

    @pytest.mark.parametrize('org_name, status_code, expected_post_delete_count', [
        ['my_org', HTTP_204_NO_CONTENT, 0],
        ['other_org', HTTP_404_NOT_FOUND, 1],
    ])
    def test_delete_membership(self, client, org_name, status_code, expected_post_delete_count):
        """
        Ensure membership deletion is possible via the API.
        """
        org = Organization.objects.get(name=org_name)
        membership = MembershipFactory.create(group__organization=org)
        UserOrganizationMapping.objects.create(user=membership.user, organization=org)
        response = client.delete('/memberships/{}/'.format(membership.id))
        assert response.status_code == status_code, response.content
        assert Membership.objects.count() == expected_post_delete_count


class TestMembershipRuleViewSet(ViewSetTestBase):
    """
    Tests for the MembershipRuleViewSet APIs.
    """

    url = '/membership-rules/'

    def test_no_rules(self, client):
        response = client.get(self.url)
        assert response.status_code == HTTP_200_OK, response.content
        results = response.json()['results']
        assert results == []

    @pytest.mark.parametrize('org_name, status_code, expected_count', [
        ['my_org', HTTP_200_OK, 3],
        ['other_org', HTTP_200_OK, 0],
    ])
    def test_list_rules(self, client, org_name, status_code, expected_count):
        org = Organization.objects.get(name=org_name)
        MembershipRuleFactory.create_batch(3, group__organization=org)
        response = client.get(self.url)
        assert response.status_code == status_code, response.content
        assert response.json()['count'] == expected_count

    @pytest.mark.parametrize('org_name, status_code, skip_response_check', [
        ['my_org', HTTP_200_OK, False],
        ['other_org', HTTP_404_NOT_FOUND, True],
    ])
    def test_one_rule(self, client, org_name, status_code, skip_response_check):
        org = Organization.objects.get(name=org_name)
        rule = MembershipRuleFactory.create(group__organization=org)
        response = client.get('/membership-rules/{}/'.format(rule.id))
        result = response.json()
        assert response.status_code == status_code, response.content
        assert skip_response_check or (result == {
            'id': rule.id,
            'name': rule.name,
            'domain': rule.domain,
            'group': {
                'id': rule.group.id,
                'name': rule.group.name,
            },
        }), 'Verify the serializer results.'

    @pytest.mark.parametrize('org_name, status_code, expected_count, check_new_rule', [
        ['my_org', HTTP_201_CREATED, 1, True],
        ['other_org', HTTP_400_BAD_REQUEST, 0, False],
    ])
    def test_add_rule(self, client, org_name, status_code, expected_count, check_new_rule):
        assert not MembershipRule.objects.count()
        org = Organization.objects.get(name=org_name)
        group = CourseAccessGroupFactory.create(organization=org)
        rule_domain = 'example.org'
        response = client.post(self.url, {
            'group': group.id,
            'name': 'Community assignment',
            'domain': rule_domain,
        })
        assert response.status_code == status_code, response.content
        assert MembershipRule.objects.count() == expected_count
        if check_new_rule:
            new_rule = MembershipRule.objects.get()
            assert new_rule.group.id == group.id
            assert new_rule.domain == rule_domain
            assert new_rule.name == 'Community assignment'

    @pytest.mark.parametrize('org_name, status_code, expected_post_delete_count', [
        ['my_org', HTTP_204_NO_CONTENT, 0],
        ['other_org', HTTP_404_NOT_FOUND, 1],
    ])
    def test_delete_rule(self, client, org_name, status_code, expected_post_delete_count):
        """
        Ensure rule deletion is possible via the API.
        """
        org = Organization.objects.get(name=org_name)
        rule = MembershipRuleFactory.create(group__organization=org)
        response = client.delete('/membership-rules/{}/'.format(rule.id))
        assert response.status_code == status_code, response.content
        assert MembershipRule.objects.count() == expected_post_delete_count


class TestGroupCourseViewSet(ViewSetTestBase):
    """
    Tests for the GroupCourseViewSet APIs.
    """

    url = '/group-courses/'

    def test_no_links(self, client):
        response = client.get(self.url)
        assert response.status_code == HTTP_200_OK
        results = response.json()['results']
        assert results == []

    @pytest.mark.parametrize('org_name, status_code, expected_count', [
        ['my_org', HTTP_200_OK, 3],
        ['other_org', HTTP_200_OK, 0],
    ])
    def test_list_links(self, client, org_name, status_code, expected_count):
        org = Organization.objects.get(name=org_name)
        course = CourseOverviewFactory.create()
        OrganizationCourse.objects.create(course_id=text_type(course.id), organization=org)
        GroupCourseFactory.create_batch(3, group__organization=org, course=course)
        response = client.get(self.url)
        assert response.status_code == HTTP_200_OK, response.content
        results = response.json()['results']
        assert len(results) == expected_count

    @pytest.mark.parametrize('org_name, status_code, skip_response_check', [
        ['my_org', HTTP_200_OK, False],
        ['other_org', HTTP_404_NOT_FOUND, True],
    ])
    def test_one_link(self, client, org_name, status_code, skip_response_check):
        org = Organization.objects.get(name=org_name)
        link = GroupCourseFactory.create(group__organization=org)
        OrganizationCourse.objects.create(course_id=text_type(link.course.id), organization=org)
        response = client.get('/group-courses/{}/'.format(link.id))
        assert response.status_code == status_code, response.content
        result = response.json()
        assert skip_response_check or (result == {
            'id': link.id,
            'course': {
                'id': text_type(link.course.id),
                'name': link.course.display_name_with_default,
            },
            'group': {
                'id': link.group.id,
                'name': link.group.name,
            },
        }), 'Verify the serializer results.'

    @pytest.mark.parametrize('group_org, course_org, status_code, expected_count, check_new_link', [
        ['my_org', 'my_org', HTTP_201_CREATED, 1, True],  # Should work for own courses and groups
        ['my_org', 'other_org', HTTP_400_BAD_REQUEST, 0, False],  # Should not work other org's courses
        ['other_org', 'my_org', HTTP_400_BAD_REQUEST, 0, False],  # Should not work for other org's groups
    ])
    def test_add_link(self, client, group_org, course_org, status_code, expected_count, check_new_link):
        assert not GroupCourse.objects.count()
        org = Organization.objects.get(name=group_org)
        group = CourseAccessGroupFactory.create(organization=org)
        course = CourseOverviewFactory.create()
        OrganizationCourse.objects.create(
            course_id=text_type(course.id),
            organization=Organization.objects.get(name=course_org),
        )
        response = client.post(self.url, {
            'group': group.id,
            'course': text_type(course.id),
        })
        assert GroupCourse.objects.count() == expected_count
        assert response.status_code == status_code, response.content
        if check_new_link:
            new_link = GroupCourse.objects.get()
            assert new_link.group.id == group.id
            assert new_link.course.id == course.id

    @pytest.mark.parametrize('org_name, status_code, expected_post_delete_count', [
        ['my_org', HTTP_204_NO_CONTENT, 0],
        ['other_org', HTTP_404_NOT_FOUND, 1],
    ])
    def test_delete_link(self, client, org_name, status_code, expected_post_delete_count):
        """
        Ensure link deletion is possible via the API.
        """
        org = Organization.objects.get(name=org_name)
        link = GroupCourseFactory.create(group__organization=org)
        response = client.delete('/group-courses/{}/'.format(link.id))
        assert response.status_code == status_code, response.content
        assert GroupCourse.objects.count() == expected_post_delete_count
