
from rest_framework import serializers

from cynerio_assignment.core.model import CynerioTask


class CynerioTaskSerializer(serializers.ModelSerializer):

	class Meta:
		model = CynerioTask
		fields = '__all__'
