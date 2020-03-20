Getting Started
===============

This guide provides minimal guide to start working on this app on devstack,
production and virtualenv environment.

Quickstart Instructions for Production
--------------------------------------
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

Quickstart Instructions for Devstack
------------------------------------

Set ``FEATURES["ORGANIZATIONS_APP"] = true`` in both ``lms.env.json``
and ``cms.env.json`` of your Docker devstack.
Set ``"ENABLE_COURSE_ACCESS_GROUPS": true`` in Site Configuration under:
http://localhost:18000/admin/site_configuration/siteconfiguration/ .

Then run the following commands on your machine:

.. code-block:: bash

    $ cd ~/work/tahoe-hawthorn/src/
    $ git clone git@github.com:appsembler/course-access-groups.git cag
    $ git clone https://github.com/appsembler/edx-search.git search
    $ cd search && git checkout appsembler-beta-release-2020-01-07_4
    $ cd ../../devstack
    $ make COMMAND='pip install -e /edx/src/cag -e /edx/src/search' tahoe.exec.edxapp
    $ make COMMAND='python manage.py lms --settings=devstack_docker migrate' SERVICE=lms tahoe.exec.single
    $ make lms-restart studio-restart

You should be able to control the CAG model from within:
http://localhost:18000/admin/course_access_groups/

Good luck fiddling with it.


If something doesn't work for you, make sure you have all the required changes
for your Open edX for. See the :ref:``supported_open_edx_version`` section for
information about those required changes.

Install Dependencies for Contributing to This App
-------------------------------------------------
If you have not already done so, create or activate a `virtualenv`_. Unless otherwise stated, assume all terminal code
below is executed within the virtualenv.

.. _virtualenv: https://virtualenvwrapper.readthedocs.org/en/latest/

Dependencies can be installed via the command below.

.. code-block:: bash

    $ make requirements
    $ pytest
