from typing import Union, Tuple

from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from cynerio_assignment.core.model import CynerioTask, UserCynerioTask
from cynerio_assignment.core.serializers import CynerioTaskSerializer


class TaskView(APIView):
	http_method_names = ['get', 'post', 'put']

	@swagger_auto_schema(
	operation_description="Retrieve a list of all tasks", responses={
			200: openapi.Response('List of tasks', CynerioTaskSerializer)}
	)
	def get(self, request: Request) -> Response:
		try:
			tasks = CynerioTask.objects.all()
			serializer = CynerioTaskSerializer(tasks, many=True)
			return Response(serializer.data, status=status.HTTP_200_OK)
		except Exception as e:
			return Response(f'Error while fetching tasks, {e}', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@swagger_auto_schema(
	operation_description="Create a new task",
	request_body=openapi.Schema(
		type=openapi.TYPE_OBJECT, properties={
			'name': openapi.Schema(type=openapi.TYPE_STRING, description="Name of the new task")}),
		responses={201: openapi.Response('Newly created task', CynerioTaskSerializer)}
	)
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

	@swagger_auto_schema(
	operation_description="Updates the status of a task",
	request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
		'task_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the task to update"),
		'active': openapi.Schema(type=openapi.TYPE_STRING, description="True or false to activate/deactivate the task"),
		'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the user performing the update"),},
								required=['task_id', 'active'],
	responses={
		200: openapi.Response('Task updated successfully', {'msg': 'Succeed'}),
		400: openapi.Response('Bad request due to invalid parameters or missing user_id', openapi.Schema(
			type=openapi.TYPE_OBJECT,
			properties={
				'msg': openapi.Schema(type=openapi.TYPE_STRING, description="Error message"),
				'identifier': openapi.Schema(type=openapi.TYPE_INTEGER, description="Newly created user ID (if user_id was missing)")
			}
		)),
		500: openapi.Response('Internal server error')},
	))
	def put(self, request: Request) -> Response:
		try:
			try:
				task_id, is_checkin = self.validate_put_params(request)
			except ValueError as e:
				return Response({'msg': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)

			user_id = request.data.get('user_id')
			random_suffix = get_random_string(length=6)

			if not user_id:
				username = f'user_{random_suffix}'
				password = get_random_string(length=12)
				new_user = User.objects.create_user(username=username, password=password)
				return Response(
					{'msg': f'Missing user_id parameter, please use the returned identifier','identifier': new_user.id},
					status=status.HTTP_400_BAD_REQUEST)

			user = get_object_or_404(User, id=user_id)
			requested_task = get_object_or_404(CynerioTask, id=task_id)
			try:
				self.validate_logic(user, task_id, requested_task, is_checkin)
			except ValueError as e:
				return Response({'msg': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)

			requested_task.is_checkin = is_checkin
			requested_task.save(user_id=user_id)
			return Response({'msg': 'Succeed'}, status=status.HTTP_200_OK)

		except Exception as e:
			return Response({'msg': f'Error while trying to update task id: {task_id}, {e}'},
							status=status.HTTP_500_INTERNAL_SERVER_ERROR)


	@staticmethod
	def validate_put_params(request: Request) -> Union[Tuple[int, bool], ValueError]:
		task_id = request.data.get('task_id')
		is_active = str(request.data.get('active', '')).lower()

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
			# In case user try to set task that belongs to other user
			if UserCynerioTask.objects.filter(task__id=task_id, task__is_checkin=True).exclude(user=user).exists():
				raise ValueError(f'This task belongs to another user!')

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
			users_report = []
			for user in users:
				user_report = dict({'id': user.id, 'tasks': []})
				user_tasks = users_tasks.filter(user=user)
				if not user_tasks:
					continue
				for user_task in user_tasks:
					time_spent = user_task.get_time_spent()
					user_report['tasks'].append({'task name:': user_task.task.name, 'time spent': time_spent})

				users_report.append(user_report)

			return Response(users_report, status=status.HTTP_200_OK)
		except Exception as e:
			return Response(f'Error while fetching tasks, {e}', status=status.HTTP_500_INTERNAL_SERVER_ERROR)