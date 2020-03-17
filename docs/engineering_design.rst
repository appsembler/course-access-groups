.. _chapter-engineering_design:

Engineering Design
==================

This section describes the design of the Course Access Groups Open edX app.
It aims to be succinct and focuses on three topics:

 * Hard-coded assumptions
 * Related extension points in Open edX
 * The internal models and their interaction

Besides a section to denote future plans for the app.


Hard-coded Assumptions
----------------------

Ideally, this app would blend into Open edX seamlessly without requiring
special configuration or dependencies. However, this level of seamless
integration may come at the cost of both complexity and reliability of
the app.

Therefore the app was designed to be somewhat simple with a couple of
hard-coded assumptions about the platform that would uses it.

While these assumptions are hard-coded in the initial release, some of them
will be revisited in future release to be either modified or completely
removed.

 * **Multi-tenancy:** One of the main assumptions is that the platform
   uses the multi-tenancy (Django Site) features without having a main site of
   its own.
 * **Dependency on edx-organizations:** In order to implement a
   full-featured multi-tenancy app, the ``edx-organizations`` is the go-to
   app to implement this feature.
 * **Access Control Backends:**
   Which allows plugins like the CAG app to
   modify the behaviour of ``courseware.access.has_access`` function
   in Open edX platform. More info is one the
   `Access Control Backends`_ pull request.
   pull request.
 * **Other app changes:** In order for the app to work it
   requires three hard-coded changes into the platform that would eventually
   be upstreamed. For more information see :ref:``supported_open_edx_version``.



Course Access Groups Database Modules
-------------------------------------

Naturally, ``course_access_groups.models`` module has the most up-to date
information and documentation about the database models.

Nevertheless, this section aims to provide a summary of the models
design. As of writing this docs, there are five distinct new models in this
app. However, when looking at the logical design we would find only three
models like the following:

The ``CourseAccessGroup`` Model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the main model which specify which learners should have
access to which courses.

This model has two Many to Many relationships:

 * **Course:** Courses that belongs to this group. To simplify the use
   relation with the Django REST Framewor it has been moved to its
   own model named ``GroupCourse``.

 * **User:** Users who are member of this group. For the same reasons above
   it has it's own model named ``Membership``.

This model is the only essential model for this app to run. The others can
be thought of as complementary.

The ``PublicCourse`` Model
~~~~~~~~~~~~~~~~~~~~~~~~~~
This model is used to mark courses as public to exempt from the
Course Access Group rules.

Instead of modifying ``CourseOverview`` to have an additional boolean field
e.g. ``CourseOverview.cag_is_public``, a new model has been created.

This necessary to avoid having complex database migration design and
minimize the maintenance impact of this app.

The ``MembershipRule`` Model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This model is used to automatically assign learners to Course Access Groups.
It utilizes the
`USER_ACCOUNT_ACTIVATED <https://github.com/edx/edx-platform/pull/23296>`_
Django signal to match learners into groups based on their email domain name.


Future Plans
------------

This application works on a *modified* fork of the Hawthorn release. This
section denotes plans to support future releases the impact on the
architecture of this app.

Supporting Bridgekeeper in Juniper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As of April, 2019 the Open edX team started to use
`Bridgekeeper <https://github.com/edx/edx-platform/pull/20250>`_ for Access
Control which eventually would deprecate the ``courseware.has_access``
function.

The plan to support Bridgekeeper is to remove the hooks for ``has_access``
and replace them with ``bridgekeeper.perms[]`` rules.

For more information about Bridgekeeper check the project documentation:
https://bridgekeeper.readthedocs.io/.

This is probably the change with the most impact. So far there's no concrete
plan to adapt to it.

In addition to this documentation please consider taking a look at the
`Access Control Backends thread`_ on Open edX Discuss.
It touches on a couple of related topics regarding Bridgekeeper and some
recommendation from the edX engineers.

Single-site Setups
~~~~~~~~~~~~~~~~~~
The majority of the Open edX Platform installations are single-site setups
in which Site Configurations isn't used. This application doesn't support
such installations at the moment. Several modifications needs to be done to
support this installation. Here are few that we are already aware of:

 - A new flag to select the mode of the app e.g.
   ``FEATURES['COURSE_ACCESS_GROUPS_IS_MULTISITE']``.

 - ``CourseAccessGroup.organization`` to be optional: This can be done in two
   methods: A) Make the field ``null=True`` or make a new
   ``SiteWideCourseAccessGroup`` to avoid having null values. My (Omar)
   preference is having a second module.

 - Some queries checks either of ``UserOrganizationMapping`` and
   ``OrganizationCourse``. Those queries won't work on the single-site setups
   so it needs to be refactored.


**Open Question:** Do we want to support both site-wide and
organization-specific mode at the same time? The initial assumption that it
would be very costly and would complicate the app. Anyway, that's still an
open question.


.. _Access Control Backends: https://github.com/appsembler/edx-platform/pull/491
.. _Access Control Backends thread: https://discuss.openedx.org/t/pluggable-access-control-both-viewing-and-enrolling-in-a-course/803
