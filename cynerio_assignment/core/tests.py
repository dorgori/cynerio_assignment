import django

django.setup()

from django.contrib.auth.models import User
from django.test import TestCase, Client, RequestFactory
from cynerio_assignment.core.model import CynerioTask, UserCynerioTask


class TestAppAdmin(TestCase):
    url_prefix = '/core/api/v1'
    client = Client()
    test_username = 'user'
    test_password = 'test_password'

    def setUp(self):
        self.factory = RequestFactory()
        self.user_1 = User.objects.create_user(username='user_1', password='pass_1')
        self.user_2 = User.objects.create_user(username='user_2', password='pass_2')

        self.task_1 = CynerioTask.objects.create(name='task_1')
        self.task_2 = CynerioTask.objects.create(name='task_2')
        self.task_3 = CynerioTask.objects.create(name='task_3')

    def test_bad_task_creation(self):
        # Expected 400, task already exists
        r = self.client.post(f'{self.url_prefix}/task/', data={}, content_type="application/json")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json(), f'Missing name parameter')

        # Expected 400, task already exists
        r = self.client.post(f'{self.url_prefix}/task/', data={'name': 'task_1'}, content_type="application/json")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json(), f'Task name task_1 is already exists')

    def test_successfully_task_creation(self):
        # Expected 201, task created
        r = self.client.post(f'{self.url_prefix}/task/', data={'name': 'task_4'}, content_type="application/json")
        self.assertEqual(r.status_code, 201)

    def test_bad_set_task_as_active(self):
        # Expected 400, no active missing active parameter
        r = self.client.put(f'{self.url_prefix}/task/', data={'task_id': '30'}, content_type="application/json")
        self.assertTrue(r.status_code, 400)
        self.assertTrue(r.json(), 'missing active parameter, should be one of [true, false]')

        # Expected 400,no user id, use identifier
        r = self.client.put(f'{self.url_prefix}/task/', data={'task_id': '30', 'active': 'true'}, content_type="application/json")
        json_obj = r.json()
        self.assertEqual(r.status_code, 400)
        self.assertEqual(json_obj['msg'], 'Missing user_id parameter, please use the returned identifier')

        # Expected 400, bad task_id parameter
        r = self.client.put(f'{self.url_prefix}/task/', data={'task_id': '30', 'active': 'true', 'user_id': json_obj['identifier']},
                            content_type="application/json")
        self.assertEqual(r.status_code, 500)
        self.assertEqual(r.json(), 'Error while trying to update task id: 30, No CynerioTask matches the given query.')

    def test_successully_set_task_as_active(self):
        # Expected 200, Succeed, and UserCynerioTask created
        r = self.client.put(f'{self.url_prefix}/task/',
                            data={'task_id': '1', 'active': 'true', 'user_id': 1},
                            content_type="application/json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), 'Succeed')
        self.assertEqual(UserCynerioTask.objects.filter(user__id=1, task__id=1, task__is_checkin=True).count(), 1)

        r = self.client.put(f'{self.url_prefix}/task/',
                            data={'task_id': '2', 'active': 'true', 'user_id': 1},
                            content_type="application/json")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json(), 'You already have a task in progress')
        r = self.client.put(f'{self.url_prefix}/task/',
                            data={'task_id': '1', 'active': 'true', 'user_id': 2},
                            content_type="application/json")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json(), 'This task is already assigned to another user')

    def test_report_api(self):
        # UserCynerioTask.objects.create(user=self.user_1, task=self.task_1)
        self.assertEqual(UserCynerioTask.objects.filter(
            user=self.user_1, task=self.task_1, task__is_checkin=True).count(), 0)

        self.task_1.is_checkin = True
        self.task_1.save(user_id=self.user_1.id)
        self.assertEqual(UserCynerioTask.objects.filter(
            user=self.user_1, task=self.task_1, task__is_checkin=True).count(), 1)
        r = self.client.get(f'{self.url_prefix}/task_report/', {})
        self.assertEqual(r.status_code, 200)