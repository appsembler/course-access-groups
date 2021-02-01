"""
A module to group all Open edX imports.
"""

from lms.djangoapps.courseware.access_utils import ACCESS_DENIED, ACCESS_GRANTED
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.lib.api.authentication import OAuth2Authentication
