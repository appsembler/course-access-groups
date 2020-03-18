Getting Started
===============

If you have not already done so, create or activate a `virtualenv`_. Unless otherwise stated, assume all terminal code
below is executed within the virtualenv.

.. _virtualenv: https://virtualenvwrapper.readthedocs.org/en/latest/


Install Dependencies for Development
------------------------------------
Dependencies can be installed via the command below.

.. code-block:: bash

    $ make requirements


Quickstart Instructions for Devstack and Production
---------------------------------------------------
Install this plugin via ``pip``. Then configure your Ansible
``server-vars.yml`` with the following:

.. code:: yaml

    ACCESS_CONTROL_BACKENDS:
      course.enroll:
        NAME: course_access_groups.acl_backends:user_has_access
      course.see_in_catalog:
        NAME: course_access_groups.acl_backends:user_has_access
      course.see_about_page:
        NAME: course_access_groups.acl_backends:user_has_access
      course.see_exists:
        NAME: course_access_groups.acl_backends:user_has_access
