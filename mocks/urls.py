"""
URLs module for development purposes.
"""
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from django.conf.urls import include, url
import course_access_groups.urls

admin.autodiscover()

urlpatterns = (
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(course_access_groups.urls)),
)
