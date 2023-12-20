from typing import Union, Tuple

from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status


from cynerio_assignment.core.model import CynerioTask, UserCynerioTask
from cynerio_assignment.core.serializers import CynerioTaskSerializer


class TaskView(APIView):
	http_method_names = ['get', 'post', 'put']
	"""
		Return all tasks

	"""
	def get(self, request: Request) -> Response:
		try:
			tasks = CynerioTask.objects.all()
			serializer = CynerioTaskSerializer(tasks, many=True)
			return Response(serializer.data, status=status.HTTP_200_OK)
		except Exception as e:
			return Response(f'Error while fetching tasks, {e}', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	"""
		Create new task

		Accepts the following parameters
		+  name: task name, str
	"""
	# API to create tasks
	def post(self, request: Request) -> Response:
		try:
			try:
				task_name = self.validate_post_params(request)
			except ValueError as e:
				return Response(f'{e}', status=status.HTTP_400_BAD_REQUEST)
			new_task = CynerioTask.objects.create(name=task_name)
			serializer = CynerioTaskSerializer(new_task)
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		except Exception as e:
			return Response(f'Error while creating new task, {e}', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	"""
		Updates task status

		Accepts the following parameters
		+  task_id: task id, int
		+  active: true/false, str
		+  user_id: user id, int
	"""
	def put(self, request: Request) -> Response:
		try:
			try:
				task_id, is_checkin = self.validate_put_params(request)
			except ValueError as e:
				return Response(f'{e}', status=status.HTTP_400_BAD_REQUEST)

			user_id = request.data.get('user_id')
			random_suffix = get_random_string(length=6)

			if not user_id:
				username = f'user_{random_suffix}'
				password = get_random_string(length=12)
				new_user = User.objects.create_user(username=username, password=password)
				return Response(
					{'msg': f'Missing user_id parameter, please use the returned identifier', 'identifier': new_user.id},
					status=status.HTTP_400_BAD_REQUEST)

			user = get_object_or_404(User, id=user_id)
			requested_task = get_object_or_404(CynerioTask, id=task_id)
			try:
				self.validate_logic(user, task_id, requested_task, is_checkin)
			except ValueError as e:
				return Response(f'{e}', status=status.HTTP_400_BAD_REQUEST)

			requested_task.is_checkin = is_checkin
			requested_task.save(user_id=user_id)
			return Response(f'Succeed', status=status.HTTP_200_OK)

		except Exception as e:
			return Response(f'Error while trying to update task id: {task_id}, {e}', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@staticmethod
	def validate_put_params(request: Request) -> Union[Tuple[int, bool], ValueError]:
		task_id = request.data.get('task_id')
		is_active = request.data.get('active', '').lower()

		if not task_id:
			raise ValueError(f'Missing task_id parameter')

		if is_active:
			if is_active not in ['true', 'false']:
				raise ValueError(f'active parameter should be one of [true, false]')
			is_checkin = is_active == 'true'
		else:
			raise ValueError(f'missing active parameter, should be one of [true, false]')

		return task_id, is_checkin

	@staticmethod
	def validate_logic(user, task_id, requested_task, is_checkin):
		if is_checkin:
			# In case this user has already active task in progress
			if UserCynerioTask.objects.filter(user=user, task__is_checkin=True).exists():
				raise ValueError(f'You already have a task in progress')
			# In case user request a task which is already assigned to another user
			if UserCynerioTask.objects.filter(task__id=task_id, task__is_checkin=True).exists():
				raise ValueError(f'This task is already assigned to another user')
		else:
			# In case user try to set inactive task as inactive
			if not requested_task.is_checkin:
				raise ValueError(f'This task is already inactive')

	@staticmethod
	def validate_post_params(request: Request) -> Union[Tuple[int, bool], ValueError]:
		task_name = request.data.get('name', '')
		if not task_name:
			raise ValueError('Missing name parameter')
		if CynerioTask.objects.filter(name=task_name).exists():
			raise ValueError(f'Task name {task_name} is already exists')

		return task_name


class CynerioTaskReportView(APIView):
	http_method_names = ['get']
	"""
		Return tasks report

	"""
	def get(self, request: Request) -> Response:
		try:
			users = User.objects.all()
			users_tasks = UserCynerioTask.objects.filter(user__in=users)
			users_report = 'User Report:'
			for user in users:
				user_tasks = users_tasks.filter(user=user)
				if not user_tasks:
					continue
				users_report += f'\n User {user.username}:'
				for user_task in user_tasks:
					time_spent = user_task.get_time_spent()
					users_report += f'\n {user_task.task.name}: {time_spent}'
			return Response(users_report, status=status.HTTP_200_OK)
		except Exception as e:
			return Response(f'Error while fetching tasks, {e}', status=status.HTTP_500_INTERNAL_SERVER_ERROR)