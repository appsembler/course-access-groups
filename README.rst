Course Access Groups
====================

|pypi-badge| |travis-badge| |codecov-badge| |doc-badge| |pyversions-badge|
|license-badge|


Overview
--------

This is a plugin for the Open edX Platform that provides the Course Access
Group functionality. It can be installed via pip with minimal configuration to
provide an admin panel to allow site administrators to create access groups
and assign courses to them.

Learners upon registration will be automatically
assigned to a specific group, from which it'll be possible to see which
courses they'll be able to see and enroll in.

The classic example is that you'd want to offer different courses to your
``customers``, ``employees`` and offer some courses for everyone. Hence you'd
need to make two groups and assign courses to only learners within those
groups while mark some courses as public ones.

Documentation
-------------

The full documentation is at https://course-access-groups.readthedocs.org.


.. _supported_open_edx_version:

Supported Open edX Version
--------------------------

The bad news, there's none. The good news is that there's a plan to make it
work with the upstream Open edX versions out of the box.

The even better news, is that you can get this plugin to work by
cherry-picking the following pull requests:

 * The `Access Control Backends pull request`_.
 * The `USER_ACCOUNT_ACTIVATED signal`_.
 * The `edx-search integration with the "has_access" function`_.

.. _Access Control Backends pull request: https://github.com/appsembler/edx-platform/pull/491
.. _USER_ACCOUNT_ACTIVATED signal: https://github.com/edx/edx-platform/pull/23296
.. _edx-search integration with the "has_access" function: https://github.com/appsembler/edx-search/pull/12

License
-------

The code in this repository is licensed under the MIT License unless
otherwise noted.

Please see ``LICENSE.txt`` for details.

How To Contribute
-----------------

Contributions are very welcome.

Even though they were written with ``edx-platform`` in mind, the guidelines
should be followed for Open edX code in general.

The pull request description template should be automatically applied if you are creating a pull request from GitHub. Otherwise you
can find it at `PULL_REQUEST_TEMPLATE.md <https://github.com/appsembler/course-access-groups/blob/master/.github/PULL_REQUEST_TEMPLATE.md>`_.

The issue report template should be automatically applied if you are creating an issue on GitHub as well. Otherwise you
can find it at `ISSUE_TEMPLATE.md <https://github.com/appsembler/course-access-groups/blob/master/.github/ISSUE_TEMPLATE.md>`_.

Reporting Security Issues
-------------------------

Please do not report security issues in public. Please email security@appsembler.com.

Getting Help
------------

Have a question about this repository, or about Open edX in general?  Please
refer to this `list of resources`_ if you need any assistance.

.. _list of resources: https://open.edx.org/getting-help


.. |pypi-badge| image:: https://img.shields.io/pypi/v/course-access-groups.svg
    :target: https://pypi.python.org/pypi/course-access-groups/
    :alt: PyPI

.. |travis-badge| image:: https://travis-ci.org/appsembler/course-access-groups.svg?branch=master
    :target: https://travis-ci.org/appsembler/course-access-groups
    :alt: Travis

.. |codecov-badge| image:: http://codecov.io/github/appsembler/course-access-groups/coverage.svg?branch=master
    :target: http://codecov.io/github/appsembler/course-access-groups?branch=master
    :alt: Codecov

.. |doc-badge| image:: https://readthedocs.org/projects/course-access-groups/badge/?version=latest
    :target: http://course-access-groups.readthedocs.io/en/latest/
    :alt: Documentation

.. |pyversions-badge| image:: https://img.shields.io/pypi/pyversions/course-access-groups.svg
    :target: https://pypi.python.org/pypi/course-access-groups/
    :alt: Supported Python versions

.. |license-badge| image:: https://img.shields.io/github/license/appsembler/course-access-groups.svg
    :target: https://github.com/appsembler/course-access-groups/blob/master/LICENSE.txt
    :alt: License
