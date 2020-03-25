#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Package metadata for course_access_groups.
"""
from __future__ import absolute_import, print_function

import os
import re
import sys

from setuptools import setup


def get_version(*file_paths):
    """
    Extract the version string from the file at the given relative path fragments.
    """
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


def load_requirements(*requirements_paths):
    """
    Load all requirements from the specified requirements files.

    Returns:
        list: Requirements file relative path strings
    """
    requirements = set()
    for path in requirements_paths:
        requirements.update(
            line.split('#')[0].strip() for line in open(path).readlines()
            if is_requirement(line.strip())
        )
    return list(requirements)


def is_requirement(line):
    """
    Return True if the requirement line is a package requirement.

    Returns:
        bool: True if the line is not blank, a comment, a URL, or an included file
    """
    return line and not line.startswith(('-r', '#', '-e', 'git+', '-c'))


VERSION = get_version('course_access_groups', '__init__.py')

if sys.argv[-1] == 'tag':
    print('Tagging the version on github:')
    os.system('git tag -a %s -m \'version %s\'' % (VERSION, VERSION))
    os.system('git push --tags')
    sys.exit()

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
CHANGELOG = open(os.path.join(os.path.dirname(__file__), 'CHANGELOG.rst')).read()

setup(
    name='course-access-groups',
    version=VERSION,
    description=(
        'An Open edX plugin to customize courses access by grouping learners '
        'and assigning different permissions to groups.'
    ),
    long_description=README + '\n\n' + CHANGELOG,
    author='Appsembler',
    author_email='omar@appsembler.com',
    url='https://github.com/appsembler/course-access-groups',
    packages=[
        'course_access_groups',
    ],
    include_package_data=True,
    install_requires=load_requirements('requirements/base.in'),
    zip_safe=False,
    keywords='Django Appsembler',
    entry_points={
        'lms.djangoapp': [
            'course_access_groups = course_access_groups.apps:CourseAccessGroupsConfig',
        ],
        'cms.djangoapp': [
            'course_access_groups = course_access_groups.apps:CourseAccessGroupsConfig',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
)
