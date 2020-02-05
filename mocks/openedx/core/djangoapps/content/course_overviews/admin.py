from django.contrib import admin
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview


@admin.register(CourseOverview)
class CourseOverviewAdmin(admin.ModelAdmin):
    """
    Dummy admin for the CourseOverview model.
    """
    pass
