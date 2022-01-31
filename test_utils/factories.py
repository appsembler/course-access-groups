# -*- coding: utf-8 -*-


import factory
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from factory.django import DjangoModelFactory
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from organizations.models import Organization, OrganizationCourse
from student.models import UserProfile
from tahoe_sites.models import UserOrganizationMapping

from course_access_groups.models import CourseAccessGroup, GroupCourse, Membership, MembershipRule, PublicCourse


class UserProfileFactory(DjangoModelFactory):
    name = factory.Sequence('Robot Mega {}'.format)

    class Meta:
        model = UserProfile


class UserFactory(DjangoModelFactory):
    email = factory.Sequence('robot{}@example.com'.format)
    username = factory.Sequence('robot{}'.format)
    profile = factory.RelatedFactory(UserProfileFactory, 'user')

    class Meta:
        model = get_user_model()


class OrganizationFactory(DjangoModelFactory):
    class Meta:
        model = Organization

    name = factory.Sequence('organization name {}'.format)
    short_name = factory.Sequence('name{}'.format)
    description = factory.Sequence('description{}'.format)
    active = True

    @factory.post_generation
    def sites(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for site in extracted:
                self.sites.add(site)


class UserOrganizationMappingFactory(DjangoModelFactory):
    class Meta:
        model = UserOrganizationMapping

    user = factory.SubFactory(UserFactory)
    organization = factory.SubFactory(OrganizationFactory)

    @classmethod
    def create_for(cls, organization, users):
        """
        Associate list of users with a certain organization.
        """
        mappings = []
        for user in users:
            mappings.append(cls.create(organization=organization, user=user))
        return mappings


class CourseAccessGroupFactory(DjangoModelFactory):
    class Meta:
        model = CourseAccessGroup

    name = factory.Sequence('Group {}'.format)
    organization = factory.SubFactory(OrganizationFactory)
    description = factory.Sequence('Group desc. {}'.format)


class MembershipFactory(DjangoModelFactory):
    class Meta:
        model = Membership

    group = factory.SubFactory(CourseAccessGroupFactory)
    user = factory.SubFactory(UserFactory)


class MembershipRuleFactory(DjangoModelFactory):
    class Meta:
        model = MembershipRule

    name = factory.Sequence('Rule {}'.format)
    domain = factory.Sequence('example{}.com'.format)
    group = factory.SubFactory(CourseAccessGroupFactory)


class CourseOverviewFactory(DjangoModelFactory):
    class Meta:
        model = CourseOverview
        django_get_or_create = ['id']

    org = factory.Sequence('org{}'.format)

    @factory.lazy_attribute
    def id(self):
        return CourseKey.from_string('course-v1:{}+toy+2012_Fall'.format(self.org))

    @factory.lazy_attribute
    def display_name(self):
        return "{} Course".format(self.id)


class OrganizationCourseFactory(DjangoModelFactory):
    class Meta:
        model = OrganizationCourse

    organization = factory.SubFactory(OrganizationFactory)

    @factory.lazy_attribute
    def course_id(self):
        course = CourseOverviewFactory.create()
        return str(course.id)

    @classmethod
    def create_for(cls, organization, courses):
        """
        Associate list of courses with a certain organization.
        """
        mappings = []
        for course in courses:
            mappings.append(cls.create(organization=organization, course_id=str(course.id)))
        return mappings


class PublicCourseFactory(DjangoModelFactory):
    class Meta:
        model = PublicCourse

    course = factory.SubFactory(CourseOverviewFactory)


class GroupCourseFactory(DjangoModelFactory):
    class Meta:
        model = GroupCourse

    group = factory.SubFactory(CourseAccessGroupFactory)
    course = factory.SubFactory(CourseOverviewFactory)


class SiteFactory(DjangoModelFactory):
    class Meta:
        model = Site

    domain = factory.Sequence(lambda n: 'site-{}.example.com'.format(n))
    name = factory.Sequence(lambda n: 'Site {}'.format(n))
