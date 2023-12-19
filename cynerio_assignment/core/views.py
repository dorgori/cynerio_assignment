from typing import Union, Tuple

from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from rest_framework.decorators import parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status


from cynerio_assignment.core.model import CynerioTask
from cynerio_assignment.core.serializers import CynerioTaskSerializer


class TaskView(APIView):
	http_method_names = ['post', 'put']

	# API to create tasks
	def post(self, request: Request) -> Response:
		try:
			# TODO:check if name is already exist..
			new_task = CynerioTask.objects.create(name=request.data.get('name'))
			serializer = CynerioTaskSerializer(new_task)
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		except Exception as e:
			return Response(f'Error while creating new task, {e}', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def put(self, request: Request) -> Response:
		try:
			try:
				task_id, is_checkin = self.validate_put_params(request)
			except ValueError as e:
				return Response(f'{e}', status=status.HTTP_400_BAD_REQUEST)

			user_id = request.data.get('user_id')
			random_suffix = get_random_string(length=6)

			# TODO:validate is_checkin param

			if not user_id:
				username = f'user_{random_suffix}'
				password = get_random_string(length=12)
				new_user = User.objects.create_user(username=username, password=password)
				return Response(
					{'msg': f'Missing user_id parameter, please use the returned identifier', 'identifier': new_user.id},
					status=status.HTTP_400_BAD_REQUEST)

			requested_task = CynerioTask.objects.filter(id=task_id)
			if requested_task:

				# TODO:check if the user has already active task, if not
				pass
			else:
				return Response(f'task id doesnt exist', status=status.HTTP_404_NOT_FOUND)
		except Exception as e:
			return Response(f'Error while trying to update task id: {task_id}, {e}', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	@staticmethod
	def validate_put_params(request: Request) -> Union[Tuple[int, bool], ValueError]:
		task_id = request.data.get('task_id')
		is_active = request.data.get('active', '').lower()
		is_checkin = False

		if not task_id:
			raise ValueError(f'Missing task_id parameter')
			# return Response(f'Missing task_id parameter', status=status.HTTP_400_BAD_REQUEST)

		if is_active:
			if is_active not in ['true', 'false']:
				raise ValueError(f'active parameter should be one of [true, false]')
			is_checkin = is_active == 'true'
		else:
			raise ValueError(f'missing active parameter, should be one of [true, false]')

		return task_id, is_checkin
