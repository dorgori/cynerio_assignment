import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cynerio_assignment")
django.setup()
import datetime
import pytest
from django.contrib.auth.models import User
from django.test import TestCase, Client, RequestFactory
from cynerio_assignment.core.model import CynerioTask, UserCynerioTask


class TestAppAdmin(TestCase):
    pytestmark = pytest.mark.django_db
    url_prefix = 'http://testserver'
    client = Client()
    test_username = 'user'
    test_password = 'test_password'

    user = None

    def setUp(self):
        self.factory = RequestFactory()
        self.user_1 = User.objects.create_user(username='user_1', password='pass_1')
        self.user_2 = User.objects.create_user(username='user_2', password='pass_2')

        self.task_1 = CynerioTask.objects.create(name='task_1')
        self.task_2 = CynerioTask.objects.create(name='task_2')
        self.task_3 = CynerioTask.objects.create(name='task_3')

        now_obj = datetime.datetime.now()
        yesterday_obj = now_obj - datetime.timedelta(days=1)
        UserCynerioTask.objects.create(user=self.user_1, task=self.task_1, last_update=now_obj.replace(minute=now_obj.minute - 15))

    def _get(self, uri, params=None):
        url = f'{self.url_prefix}/{uri}/'
        return self.client.get(url, params)

    def test_report_api(self):
        r = self._get('api/v1/report')
        response = r.json()