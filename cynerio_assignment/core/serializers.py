
from rest_framework import serializers
# from rest_framework.fields import SerializerMethodField


from cynerio_assignment.core.model import CynerioTask


class CynerioTaskSerializer(serializers.ModelSerializer):

	class Meta:
		model = CynerioTask
		fields = '__all__'




# class InternalTrainingTypeSerializer(serializers.ModelSerializer):
# 	typical_values = SerializerMethodField(source='get_typical_values')
# 	name = SerializerMethodField(source='get_name')
#
# 	class Meta:
# 		model = TrainingType
# 		fields = '__all__'
#
# 	def get_typical_values(self, obj):
# 		if obj.typical_values == {} or obj.typical_values is None:
# 			team = Team.objects.get(id=obj.team.id)
# 			team_features = get_simulator_features(team)
# 			return get_feature_empty_state(team_features)
# 		return obj.typical_values
#
# 	def get_name(self, obj):
# 		if self.context.get('internal', False) is False and not obj.in_season:
# 			return PRE_SEASON
# 		return obj.name
#
#
# class TrainingSerializer(serializers.ModelSerializer):
# 	type = SerializerMethodField(source='get_type')
# 	md_context = SerializerMethodField(source='get_md_context')
# 	use_md_context = SerializerMethodField(source='get_use_md_context')
#
# 	class Meta:
# 		model = Training
# 		fields = '__all__'
#
# 	def get_md_context(self, obj):
# 		# Were not handling mid-season and preseason !
# 		if obj.stage == obj.MIDSEASON_BREAK or obj.stage == obj.PRESEASON:
# 			return '-'
# 		distance_from_game = obj.cycle_length - obj.cycle_position
#
# 		return f'{MD}+{obj.cycle_position}/-{distance_from_game}' if distance_from_game else MD
#
# 	def get_use_md_context(self, obj):
# 		return obj.type.team.use_micro_cycle_context
#
# 	def get_type(self, obj):
# 		if self.context.get('internal') is True:
# 			return InternalTrainingTypeSerializer(obj.type).data
# 		else:
# 			return TrainingTypeSerializer(obj.type).data
#
#
# class TrainingPlanSerializer(serializers.ModelSerializer):
# 	trainings = SerializerMethodField(source='get_trainings')
#
# 	class Meta:
# 		model = TrainingPlan
# 		fields = '__all__'
#
# 	def get_trainings(self, plan):
# 		trainings = plan.trainings
# 		serialized_trainings = TrainingSerializer(trainings, many=True, context=self.context)
# 		return serialized_trainings.data
