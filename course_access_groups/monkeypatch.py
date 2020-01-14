"""
Monkey patching to address missing features from the Open edX plugin system.

Until Open edX gets pluggable course fields (imho it should), we'll have this monkey patching.
"""

from __future__ import absolute_import, unicode_literals

from logging import getLogger

from django.utils.translation import ugettext as _
from xblock.fields import List, Scope

from xmodule.course_module import CourseFields

log = getLogger(__name__)


def add_to_course_fields():
    """
    Add the `course_access_groups` Studio advanced settings by changing the CourseFields class.

    This makes every course has the new `course_access_groups` field below so it's possible to classify courses.
    This package is monkeypatching to avoid hard-coding the Course Access Group in the edX Platform itself.

    This patch is inspired by the edx-zoom XBlock monkey patching:
      - Original commit: https://github.com/edx/edx-zoom/blob/37c323ae9326/edx_zoom/apps.py#L24
    """
    cag_field = getattr(CourseFields, 'course_access_groups', None)
    if cag_field is None:  # Ensure that the field isn't added twice
        log.warning('PATCH: Monkey-patching the class CourseFields to add the `course_access_groups` field.')
        CourseFields.course_access_groups = List(
            display_name=_('Course Access Groups'),
            help=_(
                'The slugs (human readable identifiers) for the Course Access Groups which this course is'
                'available to. Enter the IDs in the following JSON array format: '
                '["employees", "customers", "university"]'
            ),
            default=[],
            scope=Scope.settings
        )
