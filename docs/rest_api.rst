.. _chapter-rest_api:

REST API Endpoints
==================

.. TODO: Move these docs into the API endpoints code documentation itself.

This plugin adds a couple of REST API endpoints to make it possible to
integrate with other systems.

The API endpoints follows a Django ViewSet conventions, so this documentation
will expand in details on one of the endpoints and be somewhat succinct on
the rest given that there's a shared pattern.

.. seealso::

    The :doc:`user_stories` section explain in details what the overall use
    cases and features of this plugin which will help to understand how to use
    the APIs better.


Course Access Groups
--------------------

These endpoints lets us to create, edit and delete Course Access Group.

List Groups
~~~~~~~~~~~
This endpoint returns a paginated list of JSON objects in "results".
Each object represents a single Course Access Group.

.. note::

    In this version there's no filtering mechanism.

.. code-block:: bash

    GET /course_access_groups/api/v1/course-access-groups/

    {
      "count": 50,
      "next": "http://mydomain.com/course_access_groups/api/v1/course-access-groups/?limit=20&offset=20",
      "previous": null,
      "results": [
        {
          "id": 1,
          "name": "Customers",
          "description": "Any customer should be enrolled here"
        },
        {
          "id": 2,
          "name": "Sales Employees",
          "description": "All team members from the sales team"
        }
      ]
    }

Group Details
~~~~~~~~~~~~~
This endpoint provides a detailed view of a single Course Access Group when
providing an group identifier (``id`` for short).


.. code-block:: bash

    GET /course_access_groups/api/v1/course-access-groups/2/

    {
      "id": 2,
      "name": "Sales Employees",
      "description": "All team members from the sales team"
    }

Add a New Group
~~~~~~~~~~~~~~~
Performing ``POST`` request to this endpoint allows to add a new group.
Both of the ``name`` and the ``description`` ``POST`` parameters are required.

.. code-block:: bash

    POST /course_access_groups/api/v1/course-access-groups/
    {"name": "New Group", "description": "My new group"}


Modify a Group
~~~~~~~~~~~~~~
To modify a group, ``PATCH`` request can be used.
Both ``name`` and ``description`` can be changed.

.. note::

    This endpoint requires a ``Content-Type: application/json`` and the
    request payload to be a properly formatted JSON object as shown below.


.. code-block:: bash

    PATCH /course_access_groups/api/v1/course-access-groups/2/
    {"name": "Awesome Group"}


Delete a Group
~~~~~~~~~~~~~~
``DELETE`` request can be used for deletion, albeit one group at a time.

.. note::

    In this version, ``DELETE`` is not idempotent, in which deleting an object
    twice will result in a 404 code for the next request. This is not really
    a problem as much as it of an issue of not conforming to the HTTP
    standards.


.. code-block:: bash

    DELETE /course_access_groups/api/v1/course-access-groups/2/

Course-Focused Course Access Group API
--------------------------------------

This API is used to retrieve course information with their Course Access Group
associations and their public status. This API is read-only.

This ViewSet is provide only the minimal course information like id and
course name. For more detailed user information or modify the courses
information other specialised APIs should be used.

List Courses
~~~~~~~~~~~~

This endpoint returns a paginated list of JSON objects in "results".
Each object represents a single course.
The course JSON also has two sub-objects ``public_status`` and
``group_links``. The inline comments will explain more the properties in more
details:


.. code-block:: javascript

    GET /course_access_groups/api/v1/group-courses/

    {
      "count": 50,
      "next": "http://mydomain.com/course_access_groups/api/v1/courses/?limit=20&offset=20",
      "previous": null,
      "results": [
        {
          "id": "course-v1:Blue+Python+2020",  // Course ID
          "name": "Introduction to Python",  // Course Name
          "public_status": {
            "is_public": false  // Either `true` or `false`
          },
          "group_links": []
        },
        {
          "id": "course-v1:Blue+SQL+2020",
          "name": "Advanced Postgres Deployments",
          "public_status": {
            "is_public": false
          },
          "group_links": [
            {
              "id": 1,  // GroupCourse linking ID to be used with the `/group-courses` API for deletion.
              "group": {
                "id": 1,  // Course Access Group ID
                "name": "Employees"  // Course Access Group name
              }
            }
          ]
        },
        {
          "id": "course-v1:Blue+Coding+101",
          "name": "Coding 101",
          "public_status": {
            "id": 1,  // PublicCourse status ID. Can be deleted via `/public-courses/`
            "is_public": true
          },
          "group_links": []
        }
      ]
    }


Linking Courses to Course Access Groups
---------------------------------------

These endpoints lets us to add and remove courses from Course Access Groups.


List Links
~~~~~~~~~~
This endpoint returns a paginated list of JSON objects in "results".
Each object represents a single a course link to a Course Access Group. The
term "link" is only used for documentation purposes instead of the technical
name ``Group Course``.
Each link JSON has a single property ``id`` which can be used to delete
the link. The link JSON also has two sub-objects representing a course and a
Course Access Group.


.. code-block:: bash

    GET /course_access_groups/api/v1/group-courses/

    {
      "count": 50,
      "next": "http://mydomain.com/course_access_groups/api/v1/group-courses/?limit=20&offset=20",
      "previous": null,
      "results": [
        {
          "id": 1,
          "course": {
            "id": "course-v1:Red+Python+2020",
            "name": "Introduction to Python"
          },
          "group": {
            "id": 1,
            "name": "Customers"
          }
        },
        {
          "id": 2,
          "course": {
            "id": "course-v1:Blue+SQL+2020",
            "name": "Advanced Postgres Deployments"
          },
          "group": {
            "id": 2,
            "name": "Employees"
          }
        }
      ]
    }


Adding, Modifying and Deleting Links
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


The link (``Group Course``) endpoints lets us to add, modify and delete
the links in a similar way to the Course Access Groups API endpoints.

To add a new link make ``POST`` request with a JSON payload:

.. note::

    The ``group`` parameter is the Course Access Group ``id`` property which
    can be obtained from the Course Access Groups list API endpoint.
    Similarly the ``course`` parameter is the course identifier.


.. code-block:: bash

    POST /course_access_groups/api/v1/group-courses/
    {"course": "course-v1:Red+Python+2020", "group": 2}

To modify a link ``PATCH`` request should be used:

    POST /course_access_groups/api/v1/group-courses/2/
    {"course": "course-v1:Blue+Python+2020_Fall"}

To delete a link:

.. code-block:: bash

    DELETE /course_access_groups/api/v1/group-courses/2/


Setting Courses as Public
-------------------------
When the course access group feature is enabled, by default all courses are
private and only accessible to learners with memberships to groups that
have those courses.

However, some users could have no group membership so they won't have access
to the private courses. To make a course available to both learners with and
without a group membership a course should be made public.

This endpoint sets the course to be public.

List Public Courses
~~~~~~~~~~~~~~~~~~~

This endpoint returns a paginated list of JSON objects in "results".
Each JSON object represents a course being public.
Each JSON object has a single property ``id`` which can be used to
make the course private.
The JSON object also has a sub-object representing a course.


.. code-block:: bash

    GET /course_access_groups/api/v1/public-courses/

    {
      "count": 50,
      "next": "http://mydomain.com/course_access_groups/api/v1/public-courses/?limit=20&offset=20",
      "previous": null,
      "results": [
        {
          "id": 9,
          "course": {
            "id": "course-v1:Red+Python+2020",
            "name": "Introduction to Python"
          }
        },
        {
          "id": 10,
          "course": {
            "id": "course-v1:Blue+SQL+2020",
            "name": "Advanced Postgres Deployments"
          }
        }
      ]
    }

Making a Course Public or Private
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``POST`` request can be used to make a course public with the following
JSON payload format:

.. note::

    The ``course`` parameter is the Course ``id`` property which
    can be obtained from the Course API endpoint.

.. code-block:: bash

    POST /course_access_groups/api/v1/public-courses/
    {"course": "course-v1:Red+Python+2020"}

To make a course private:

.. code-block:: bash

    DELETE /course_access_groups/api/v1/public-courses/10/


Membership in Course Access Groups
----------------------------------

This endpoint lets us to add and remove users from Course Access Groups.

List Memberships
~~~~~~~~~~~~~~~~

This endpoint returns a paginated list of JSON objects in "results".
Each object represents a single user membership in a Course Access Group.
Each membership JSON has a single property ``id`` which can be used to delete
the membership.
The membership JSON also has two sub-objects representing a user and a
Course Access Group.


.. code-block:: bash

    GET /course_access_groups/api/v1/memberships/

    {
      "count": 50,
      "next": "http://mydomain.com/course_access_groups/api/v1/memberships/?limit=20&offset=20",
      "previous": null,
      "results": [
        {
          "id": 5,
          "user": {
            "id": 2,
            "username": "ali",
            "email": "ali@corp.com"
          },
          "group": {
            "id": 1,
            "name": "Employees"
          }
        },
        {
          "id": 6,
          "user": {
            "id": 3,
            "username": "Mike",
            "email": "mike@customer.com"
          },
          "group": {
            "id": 2,
            "name": "Customers"
          }
        }
      ]
    }

Adding, Modifying and Deleting Memberships
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


The membership endpoints lets us add, modify and delete
the memberships in a similar way to the Course Access Groups API endpoints.

To add a new membership make ``POST`` request with a JSON payload:

.. note::

    The ``group`` parameter is the Course Access Group ``id`` property which
    can be obtained from the Course Access Groups list API endpoint.
    Similarly the ``user`` parameter is the user identifier.


.. code-block:: bash

    POST /course_access_groups/api/v1/memberships/
    {"user": 857, "group": 2}

To modify a membership ``PATCH`` request should be used.

.. note::

    A user can have a membership to a single group.

    POST /course_access_groups/api/v1/memberships/5/
    {"group": 3}

To delete a membership:

.. code-block:: bash

    DELETE /course_access_groups/api/v1/memberships/5/


User-Focused Course Access Group API
------------------------------------

This API is used to retrieve user information with their Course Access Group
associations. This API is a read-only API.

This ViewSet is provide only the minimal user information like email and
username. For more detailed user information or modify the membership
information other specialised APIs should be used.

List Users
~~~~~~~~~~

This endpoint returns a paginated list of JSON objects in "results".
Each object represents a single user in your organization.
Each user JSON has a few personal information like ``email`` and ``username``.
The user JSON also has a sub-object ``membership`` in a Course Access Group.
The inline comments will explain in more details:

Query Parameters
````````````````

This endpoint supports the following query parameters e.g.
``/course_access_groups/api/v1/users/?search=corp.com``

===========   =======   ===============
Name          Type      Description
===========   =======   ===============
search        string    Search for any text within the name, username and
                        email of the user data.
email_exact   string    Search for case-insensitive exact matches of a
                        user email.
group         number    Filter by Course Access Group ID.
no_group      boolean   Use ``True`` to filter users with no group
                        association. On the other hand ``False`` would filter
                        all users with *any* group association.
===========   =======   ===============

.. code-block:: javascript

    GET /course_access_groups/api/v1/users/

    {
      "count": 50,
      "next": "http://mydomain.com/course_access_groups/api/v1/users/?limit=20&offset=20",
      "previous": null,
      "results": [
        {
          "id": 2,  // The User ID that can be used in the `/memberships/` endpoint
          "username": "ali",  // The short public username used in forums
          "name": "Ali Al-Ithawi",  // The full name used in certificates
          "email": "ali@corp.com",
          "membership": {  // Membership information
            "id": 5,  // Use this `membership` ID to delete the membership via the `/memberships/` endpoint.
            "group": {
              "id": 1,  // The Course Access Group ID
              "name": "Employees"  // The Course Access Group name
            }
          }
        },
        {
          "id": 2,
          "username": "johnb",
          "name": "John Baldwin",
          "email": "john@community.org",
          "membership": null  // This user has no membership
        }
    }


Rules for Automatic User Membership
-----------------------------------

These endpoints lets us to manage rules for automatic membership based on
email address.

.. note::

    The membership rules are only activated after the learner (user)
    activates their email address. Before that, the learner will be considered
    as without a group.

List Membership Rules
~~~~~~~~~~~~~~~~~~~~~

This endpoint returns a paginated list of JSON objects in "results".
Each object represents a single membership rule.
Besides the ``id`` and the ``name`` properties, each rule JSON has a
``domain`` which is the email domain name to match the users for.


The membership rule JSON also has a sub-object representing a
Course Access Group.


.. code-block:: bash

    GET /course_access_groups/api/v1/membership-rules/

    {
      "count": 50,
      "next": "http://mydomain.com/course_access_groups/api/v1/membership-rules/?limit=20&offset=20",
      "previous": null,
      "results": [
        {
          "id": 8,
          "name": "Assign customers",
          "domain": "customer1.xyz",
          "group": {
            "id": 1,
            "name": "Customers"
          }
        },
        {
          "id": 9,
          "name": "Assign another customer",
          "domain": "company2.xyz.uk",
          "group": {
            "id": 1,
            "name": "Customers"
          }
        }
      ]
    }

Adding, Modifying and Deleting Memberships
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


The membership rule endpoints lets us to add, modify and delete
the membership rules in a similar way to the Course Access Groups
API endpoints.

To add a new membership rule make ``POST`` request with a JSON payload:

.. note::

    The ``group`` parameter is the Course Access Group ``id`` property which
    can be obtained from the Course Access Groups list API endpoint.


.. code-block:: bash

    POST /course_access_groups/api/v1/membership-rules/
    {"name": "XYZ Customers", "domain": "company.xyz", "group": 2}

To modify a membership rule ``PATCH`` request should be used.

    POST /course_access_groups/api/v1/membership-rules/5/
    {"group": 3}

To delete a membership rule:

.. code-block:: bash

    DELETE /course_access_groups/api/v1/membership-rules/5/
