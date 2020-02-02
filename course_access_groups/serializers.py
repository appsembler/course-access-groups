from rest_framework import serializers

from course_access_groups.models import (
    CourseAccessGroup,
)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseAccessGroup
        fields = [
            'id', 'name', 'description',
        ]
