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


Linking Courses to Course Access Groups
---------------------------------------

These endpoints lets us to add and remove courses from Course Access Groups.


.. note::

    This section is a work in progress.


Marking Courses as Public
-------------------------

These endpoints allow mark courses as a public.
This means the course is available to
all site learners regardless of their Course Access Groups membership.

.. note::

    This section is a work in progress.



User Membership in Course Access Groups
---------------------------------------

These endpoints lets us to add and remove users from Course Access Groups.


.. note::

    This section is a work in progress.


Rules for Automatic User Membership
-----------------------------------

These endpoints lets us to manage rules for automatic membership based on
email address.


.. note::

    The membership rules are only activated after the learner (user)
    activates their email address. Before that, the learner will be considered
    as without a group.


.. note::

    This section is a work in progress.