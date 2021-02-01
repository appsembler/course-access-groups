# -*- coding: utf-8 -*-
"""
Tests for the feature flag helper.
"""


import pytest
from course_access_groups.feature_flag import ConfigurationError, is_feature_enabled
from test_utils import patch_site_configs


@pytest.mark.parametrize('expected_feature_enabled', [False, True])
def test_is_feature_enabled(settings, expected_feature_enabled):
    """
    Ensure `is_feature_enabled()` respects the `ENABLE_COURSE_ACCESS_GROUPS` Site Configuration value.
    """

    settings.FEATURES['ORGANIZATIONS_APP'] = True

    with patch_site_configs({'ENABLE_COURSE_ACCESS_GROUPS': expected_feature_enabled}):
        assert is_feature_enabled() == expected_feature_enabled


def test_is_feature_disabled_org_disabled(settings):
    """
    Ensure `is_feature_enabled()` returns False when both Org App and the feature flag is disabled.
    """

    settings.FEATURES['ORGANIZATIONS_APP'] = False

    with patch_site_configs({'ENABLE_COURSE_ACCESS_GROUPS': False}):
        assert not is_feature_enabled()


def test_is_feature_enabled_but_orgs_disabled(settings):
    """
    Ensure `is_feature_enabled()` panic with an exception when Org App is disabled but the feature flag is enabled.
    """

    settings.FEATURES['ORGANIZATIONS_APP'] = False

    with patch_site_configs({'ENABLE_COURSE_ACCESS_GROUPS': True}):
        with pytest.raises(ConfigurationError):
            is_feature_enabled()  # Should throw configuration error due to missing organization app.
