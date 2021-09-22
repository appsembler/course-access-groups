Change Log
----------

..
   All enhancements and patches to course_access_groups will be documented
   in this file.  It adheres to the structure of http://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (http://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
~~~~~~~~~~

 * Added tests for modifying membership rule.
 * Fixed documentation for modifying the membership rule.

[0.5.1] - 2021-09-01
~~~~~~~~~~~~~~~~~~~~

Added
_____

* log exceptions for the USER_ACCOUNT_ACTIVATED signal


[0.5.0] - 2021-07-14
~~~~~~~~~~~~~~~~~~~~

Added
_____

 * Fixes for Django 2.x

Removed
_______

 * Dropped support for Python 2.x and Django 1.x

[0.4.0] - 2021-01-27
~~~~~~~~~~~~~~~~~~~~

Added
_____

* Support python3 and django2

[0.3.0] - 2020-04-06
~~~~~~~~~~~~~~~~~~~~

Added
_____

* Added new APIs /courses/ and /users/
* Few bug fixes


[0.2.0] - 2020-03-11
~~~~~~~~~~~~~~~~~~~~

Added
_____

* First release to be ready for deployment in staging environments.

[0.1.0] - 2019-11-26
~~~~~~~~~~~~~~~~~~~~

Added
_____

* First release on PyPI.
