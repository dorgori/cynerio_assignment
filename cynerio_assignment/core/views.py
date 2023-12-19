from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status


from cynerio_assignment.model import CynerioTask


class CreateTask(APIView):
	http_method_names = ['post']

	def post(self, request) -> Response:
		try:
			new_task = CynerioTask.objects.create(name=request.POST.get('name'))
			return Response(new_task, status=status.HTTP_201_CREATED)
		except Exception as e:
			return Response(f'Error while creating new task, {e}', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
