# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-03-25 03:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('course_access_groups', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupcourse',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_courses', to='course_overviews.CourseOverview'),
        ),
    ]