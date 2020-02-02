# -*- coding: utf-8 -*-
"""
Serializers to be used in APIs.

Copied from the Open edX Platform.
"""
from __future__ import absolute_import, unicode_literals

from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from rest_framework import serializers


class CourseKeyField(serializers.Field):
    """ Serializer field for a model CourseKey field. """

    def to_representation(self, data):
        """Convert a course key to unicode. """
        return unicode(data)

    def to_internal_value(self, data):
        """Convert unicode to a course key. """
        try:
            return CourseKey.from_string(data)
        except InvalidKeyError as ex:
            raise serializers.ValidationError('Invalid course key: {msg}'.format(msg=str(ex)))
