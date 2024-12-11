from rest_framework import serializers
from .models import *
from user.models import User

class ProjectSerializers(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

class DodSerializers(serializers.ModelSerializer):
    class Meta:
        model = DoD
        fields = '__all__'

class TopicsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Topics
        fields = '__all__'

class SubtaskSerializers(serializers.ModelSerializer):
    class Meta:
        model = SubTasks
        fields = '__all__'

class MembersSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id',"email","fullname","photo"]

class TaskSerializers(serializers.ModelSerializer):
    project = ProjectSerializers()
    dod = DodSerializers(many=True)
    topics = TopicsSerializers(many=True)
    subtasks = SubtaskSerializers(many=True)
    members = MembersSerializers(many=True)

    class Meta:
        model = Task
        fields = '__all__'