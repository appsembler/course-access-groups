# -*- coding: utf-8 -*-
"""
Tests for the CAG API ViewSets.
"""


import json
from six import text_type
import pytest

from django.contrib.auth import get_user_model
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from organizations.models import Organization, OrganizationCourse, UserOrganizationMapping
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from course_access_groups.models import (
    CourseAccessGroup,
    GroupCourse,
    Membership,
    MembershipRule,
    PublicCourse,
)
from test_utils.factories import (
    CourseOverviewFactory,
    MembershipFactory,
    MembershipRuleFactory,
    GroupCourseFactory,
    OrganizationCourseFactory,
    PublicCourseFactory,
    UserOrganizationMappingFactory,
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


class TestUserViewSet(ViewSetTestBase):
    """
    Tests for the UserViewSet APIs.
    """

    url = '/users/'

    def test_no_users(self, client):
        response = client.get(self.url)
        assert response.status_code == HTTP_200_OK
        results = response.json()['results']
        assert results == []

    @pytest.mark.parametrize('org_name, expected_count', [
        ['my_org', 5],
        ['other_org', 0],
    ])
    def test_list_users(self, client, org_name, expected_count):
        org = Organization.objects.get(name=org_name)
        # Two users without memberships
        without_memberships = UserFactory.create_batch(2)
        # Three additional users with memberships
        with_memberships = [m.user for m in MembershipFactory.create_batch(3, group__organization=org)]
        UserOrganizationMappingFactory.create_for(
            org,
            users=without_memberships + with_memberships,
        )
        response = client.get(self.url)
        results = response.json()['results']
        assert response.status_code == HTTP_200_OK, response.content
        assert len(results) == expected_count

    @pytest.mark.parametrize('org_name, status_code, skip_response_check', [
        ['my_org', HTTP_200_OK, False],
        ['other_org', HTTP_404_NOT_FOUND, True],
    ])
    def test_one_user_no_membership(self, client, org_name, status_code, skip_response_check):
        """
        Test JSON format for users without memberships.
        """
        org = Organization.objects.get(name=org_name)
        user = UserFactory.create()
        UserOrganizationMappingFactory.create(user=user, organization=org)
        response = client.get('{}{}/'.format(self.url, user.id))
        assert response.status_code == status_code, response.content
        result = response.json()
        assert skip_response_check or (result == {
            'id': user.id,
            'email': user.email,
            'name': user.profile.name,
            'username': user.username,
            'membership': None,
        }), 'Verify the serializer results.'

    def test_one_user_with_membership(self, client):
        """
        Test JSON format for a user with membership.
        """
        user = UserFactory.create()
        UserOrganizationMappingFactory.create(user=user, organization=self.my_org)
        membership = MembershipFactory.create(group__organization=self.my_org, user=user)
        response = client.get('{}{}/'.format(self.url, user.id))
        assert response.status_code == HTTP_200_OK, response.content
        result = response.json()
        assert result == {
            'id': user.id,
            'email': user.email,
            'name': user.profile.name,
            'username': user.username,
            'membership': {
                'id': membership.id,
                'group': {
                    'id': membership.group.id,
                    'name': membership.group.name,
                }
            },
        }, 'Verify the serializer results.'


class TestUserViewSetFilters(ViewSetTestBase):
    """
    Tests for the UserViewSet API filters.
    """

    url = '/users/'
    non_member_email = 'non_member@example.com'
    member_email = 'member@example.com'

    @pytest.fixture(autouse=True)
    def users_setup(self):
        omar = UserFactory.create(email=self.non_member_email)
        user1 = MembershipFactory.create(user__email=self.member_email).user
        user2 = MembershipFactory.create().user
        UserOrganizationMappingFactory.create_for(
            self.my_org,
            users=[omar, user1, user2],
        )

    def test_search_filter(self, client):
        response = client.get('{}?search={}'.format(self.url, 'non_member'))
        results = response.json()['results']
        assert len(results) == 1, response.content
        assert results[0]['email'] == self.non_member_email, response.content

    def test_no_group_filter(self, client):
        response = client.get('{}?no_group={}'.format(self.url, 'True'))
        results = response.json()['results']
        assert len(results) == 1, response.content
        assert results[0]['email'] == self.non_member_email, response.content

    def test_group_id_filter(self, client):
        user = get_user_model().objects.get(email=self.member_email)
        group = user.membership.group
        response = client.get('{}?group={}'.format(self.url, group.id))
        results = response.json()['results']
        assert len(results) == 1, response.content
        assert results[0]['email'] == user.email, response.content


class TestCourseViewSet(ViewSetTestBase):
    """
    Tests for the CourseViewSet APIs.
    """

    url = '/courses/'

    def test_no_courses(self, client):
        response = client.get(self.url)
        assert response.status_code == HTTP_200_OK
        results = response.json()['results']
        assert results == []

    @pytest.mark.parametrize('org_name, expected_count', [
        ['my_org', 5],
        ['other_org', 0],
    ])
    def test_list_courses(self, client, org_name, expected_count):
        org = Organization.objects.get(name=org_name)
        private_courses = CourseOverviewFactory.create_batch(2)
        GroupCourseFactory.create_batch(2, course=private_courses[0], group__organization=org)
        public_courses = [p.course for p in PublicCourseFactory.create_batch(3)]
        OrganizationCourseFactory.create_for(
            org,
            courses=private_courses + public_courses,
        )
        response = client.get(self.url)
        results = response.json()['results']
        assert response.status_code == HTTP_200_OK, response.content
        assert len(results) == expected_count

    @pytest.mark.parametrize('org_name, status_code, skip_response_check', [
        ['my_org', HTTP_200_OK, False],
        ['other_org', HTTP_404_NOT_FOUND, True],
    ])
    def test_one_course_empty_info(self, client, org_name, status_code, skip_response_check):
        """
        Test JSON format for course without course access groups info.
        """
        org = Organization.objects.get(name=org_name)
        course = CourseOverviewFactory.create()
        OrganizationCourse.objects.create(
            course_id=text_type(course.id),
            organization=org,
        )
        response = client.get('{}{}/'.format(self.url, course.id))
        assert response.status_code == status_code, response.content
        result = response.json()
        assert skip_response_check or (result == {
            'id': text_type(course.id),
            'name': course.display_name,
            'public_status': {
                'is_public': False,
            },
            'group_links': [],
        }), 'Verify the serializer results.'

    def test_one_course_full_info(self, client):
        """
        Test JSON format for course with course access groups info.
        """
        public_course = PublicCourseFactory.create()
        course = public_course.course
        OrganizationCourse.objects.create(
            course_id=text_type(course.id),
            organization=self.my_org,
        )
        group_course = GroupCourseFactory.create(course=course, group__organization=self.my_org)
        response = client.get('{}{}/'.format(self.url, course.id))
        assert response.status_code == HTTP_200_OK, response.content
        result = response.json()
        assert result == {
            'id': text_type(course.id),
            'name': course.display_name,
            'public_status': {
                'id': public_course.id,
                'is_public': True,
            },
            'group_links': [{
                'id': group_course.id,
                'group': {
                    'id': group_course.group.id,
                    'name': group_course.group.name,
                }
            }],
        }, 'Verify the serializer results.'


class TestCourseViewSetFilters(ViewSetTestBase):
    """
    Tests for the CourseOverviewViewSet API filters.
    """

    url = '/courses/'
    public_course = 'Course: Public Course'
    private_course = 'Course: I have no groups'
    group_course = 'Course: I am in a Group'

    @pytest.fixture(autouse=True)
    def users_setup(self):
        public = PublicCourseFactory.create(course__display_name=self.public_course).course
        private = CourseOverviewFactory.create(display_name=self.private_course)
        link = GroupCourseFactory.create(
            course__display_name=self.group_course,
            group__organization=self.my_org,
        )
        in_group = link.course
        OrganizationCourseFactory.create_for(self.my_org, courses=[public, private, in_group])

    def test_search_filter(self, client):
        public = CourseOverview.objects.get(display_name=self.public_course)
        response = client.get('{}?search={}'.format(self.url, public.id))
        results = response.json()['results']
        assert len(results) == 1, response.content
        assert results[0]['name'] == self.public_course, response.content

    def test_no_group_and_is_public_filter(self, client):
        response = client.get('{}?no_group=True&is_public=False'.format(self.url))
        results = response.json()['results']
        assert len(results) == 1, response.content
        assert results[0]['name'] == self.private_course, response.content

    def test_group_id_filter(self, client):
        in_group = CourseOverview.objects.get(display_name=self.group_course)
        group = in_group.group_courses.get().group
        response = client.get('{}?group={}'.format(self.url, group.id))
        results = response.json()['results']
        assert len(results) == 1, response.content
        assert results[0]['name'] == self.group_course, response.content


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


class TestPublicCourseViewSet(ViewSetTestBase):
    """
    Tests for the PublicCourseViewSet APIs.

    The word "flag" here is short for "PublicCourse flag".
    """

    url = '/public-courses/'

    def test_no_flags(self, client):
        """
        Sanity check for an empty list of PublicCourse flags.
        """
        response = client.get(self.url)
        assert response.status_code == HTTP_200_OK
        results = response.json()['results']
        assert results == []

    @pytest.mark.parametrize('org_name, status_code, expected_count', [
        ['my_org', HTTP_200_OK, 3],
        ['other_org', HTTP_200_OK, 0],
    ])
    def test_list_flags(self, client, org_name, status_code, expected_count):
        """
        List flags correctly with permissions checks.
        """
        org = Organization.objects.get(name=org_name)
        courses = [flag.course for flag in PublicCourseFactory.create_batch(3)]
        _course_org_links = [  # noqa: F841
            OrganizationCourse.objects.create(course_id=text_type(course.id), organization=org)
            for course in courses
        ]
        response = client.get(self.url)
        assert response.status_code == HTTP_200_OK, response.content
        results = response.json()['results']
        assert len(results) == expected_count

    @pytest.mark.parametrize('org_name, status_code, skip_response_check', [
        ['my_org', HTTP_200_OK, False],
        ['other_org', HTTP_404_NOT_FOUND, True],
    ])
    def test_one_flag(self, client, org_name, status_code, skip_response_check):
        """
        Check serialized PublicCourse flag.
        """
        org = Organization.objects.get(name=org_name)
        flag = PublicCourseFactory.create()
        OrganizationCourse.objects.create(course_id=text_type(flag.course.id), organization=org)
        response = client.get('/public-courses/{}/'.format(flag.id))
        assert response.status_code == status_code, response.content
        result = response.json()
        assert skip_response_check or (result == {
            'id': flag.id,
            'course': {
                'id': text_type(flag.course.id),
                'name': flag.course.display_name_with_default,
            },
        }), 'Verify the serializer results.'

    @pytest.mark.parametrize('org_name, status_code, expected_count, check_new_flag, message', [
        ['my_org', HTTP_201_CREATED, 1, True, 'Should work for own courses'],
        ['other_org', HTTP_400_BAD_REQUEST, 0, False, 'Should not work for other org courses'],
    ])
    def test_add_flag(self, client, org_name, status_code, expected_count, check_new_flag, message):
        """
        Check API POST to add new PublicCourse flag.
        """
        assert not PublicCourse.objects.count()
        org = Organization.objects.get(name=org_name)
        course = CourseOverviewFactory.create()
        OrganizationCourse.objects.create(
            course_id=text_type(course.id),
            organization=org,
        )
        response = client.post(self.url, {
            'course': text_type(course.id),
        })
        assert PublicCourse.objects.count() == expected_count, message
        assert response.status_code == status_code, response.content
        if check_new_flag:
            new_flag = PublicCourse.objects.get()
            assert new_flag.course.id == course.id

    @pytest.mark.parametrize('org_name, status_code, expected_post_delete_count', [
        ['my_org', HTTP_204_NO_CONTENT, 0],
        ['other_org', HTTP_404_NOT_FOUND, 1],
    ])
    def test_delete_flag(self, client, org_name, status_code, expected_post_delete_count):
        """
        Ensure PublicCourse flag deletion is possible via the API.
        """
        org = Organization.objects.get(name=org_name)
        flag = PublicCourseFactory.create()
        OrganizationCourse.objects.create(
            course_id=text_type(flag.course.id),
            organization=org,
        )
        response = client.delete('/public-courses/{}/'.format(flag.id))
        assert response.status_code == status_code, response.content
        assert PublicCourse.objects.count() == expected_post_delete_count


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
