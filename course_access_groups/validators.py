# -*- coding: utf-8 -*-
"""
Validation helpers for models of course_access_groups.
"""

from __future__ import absolute_import, unicode_literals

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import ugettext as _


def validate_domain(value):
    """
    Validate a domain name.

    :param value: The domain name.
    :raise ValidationError: When the domain is not valid.
    """
    domain_regex = validate_email.domain_regex
    if not domain_regex.match(value):
        raise ValidationError(_('The domain name is not valid: {domain}').format(domain=value))
