"""
Mocks for the courseware.access_utils Open edX module.
"""

from lms.djangoapps.courseware.access_response import AccessResponse

ACCESS_GRANTED = AccessResponse(True)
ACCESS_DENIED = AccessResponse(False)
