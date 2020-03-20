# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import factory
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from course_access_groups.models import (
    CourseAccessGroup,
    GroupCourse,
    Membership,
    MembershipRule,
    PublicCourse,
)
from organizations.models import Organization, UserOrganizationMapping


class UserFactory(factory.DjangoModelFactory):
    email = factory.Sequence('robot{}@example.com'.format)
    username = factory.Sequence('robot{}'.format)

    class Meta(object):
        model = get_user_model()

    class Params(object):
        organization = None


class OrganizationFactory(factory.DjangoModelFactory):
    class Meta(object):
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


class UserOrganizationMappingFactory(factory.DjangoModelFactory):
    class Meta(object):
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


class CourseAccessGroupFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = CourseAccessGroup

    name = factory.Sequence('Group {}'.format)
    organization = factory.SubFactory(OrganizationFactory)
    description = factory.Sequence('Group desc. {}'.format)


class MembershipFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = Membership

    group = factory.SubFactory(CourseAccessGroupFactory)
    user = factory.SubFactory(UserFactory)


class MembershipRuleFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = MembershipRule

    name = factory.Sequence('Rule {}'.format)
    domain = factory.Sequence('example{}.com'.format)
    group = factory.SubFactory(CourseAccessGroupFactory)


class CourseOverviewFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = CourseOverview
        django_get_or_create = ['id']

    org = factory.Sequence('org{}'.format)

    @factory.lazy_attribute
    def id(self):
        return CourseKey.from_string('course-v1:{}+toy+2012_Fall'.format(self.org))

    @factory.lazy_attribute
    def display_name(self):
        return "{} Course".format(self.id)


class PublicCourseFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = PublicCourse

    course = factory.SubFactory(CourseOverviewFactory)


class GroupCourseFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = GroupCourse

    group = factory.SubFactory(CourseAccessGroupFactory)
    course = factory.SubFactory(CourseOverviewFactory)


class SiteFactory(factory.DjangoModelFactory):
    class Meta:
        model = Site

    domain = factory.Sequence(lambda n: 'site-{}.example.com'.format(n))
    name = factory.Sequence(lambda n: 'Site {}'.format(n))

