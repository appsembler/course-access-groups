"""
URLs module for development purposes.
"""


from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path

admin.autodiscover()

urlpatterns = [
    path(r'admin/', admin.site.urls),
    url(r'^', include('course_access_groups.urls')),
]
