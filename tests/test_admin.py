"""
Tests for the admin submodule.
"""
from course_access_groups import admin


def test_admin():
    """
    Make sure the admin module works.
    """
    assert bool(admin)
