
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from cynerio_assignment.core.model import CynerioTask, UserCynerioTask


class CynerioTaskSerializer(serializers.ModelSerializer):

	class Meta:
		model = CynerioTask
		fields = '__all__'
