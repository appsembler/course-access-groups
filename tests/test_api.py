import unittest
from django.test import Client
import pytest


@pytest.mark.django_db
class GroupsTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def test_urls(self):
        response = self.client.get('/api/course_access_groups/v1/groups/')
        assert response.status_code == 200
