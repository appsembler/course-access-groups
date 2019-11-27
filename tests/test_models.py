#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for the `course-access-groups` models module.
"""

from __future__ import absolute_import, unicode_literals

from course_access_groups import acl_backends, models, urls


def test_fake():
    """
    Just a fake unit test case.
    """
    assert acl_backends
    assert models
    assert urls
