# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import factory
from django.contrib.auth import get_user_model
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from course_access_groups.models import (
    Group,
    CourseGroup,
    Membership,
    Rule,
)
from organizations.models import Organization


class UserFactory(factory.DjangoModelFactory):
    email = factory.Sequence('robot{}@example.com'.format)
    username = factory.Sequence('robot{}'.format)

    class Meta(object):
        model = get_user_model()


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


class GroupFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = Group

    name = factory.Sequence('Group {}'.format)
    organization = factory.SubFactory(OrganizationFactory)
    description = factory.Sequence('Group desc. {}'.format)


class MembershipFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = Membership

    group = factory.SubFactory(GroupFactory)
    user = factory.SubFactory(UserFactory)


class RuleFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = Rule

    name = factory.Sequence('Rule {}'.format)
    domain = factory.Sequence('example{}.com'.format)
    group = factory.SubFactory(GroupFactory)


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


class CourseGroupFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = CourseGroup

    group = factory.SubFactory(GroupFactory)
    course = factory.SubFactory(CourseOverviewFactory)