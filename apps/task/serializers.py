from rest_framework import serializers
from .models import *
from user.models import User
from user.serializers import UserGetAndDetailSerializers
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


class FileTaksSerizlisers(serializers.ModelSerializer):
    class Meta:
        model  = FileTaks
        fields = '__all__'

class CommentsSerizlisers(serializers.ModelSerializer):
    user = UserGetAndDetailSerializers()
    class Meta:
        model  = Comment
        fields = '__all__'

class TaskSerializers(serializers.ModelSerializer):
    project = ProjectSerializers()
    dod = DodSerializers(many=True)
    topics = TopicsSerializers(many=True)
    subtasks = SubtaskSerializers(many=True)
    members = MembersSerializers(many=True)
    files = FileTaksSerizlisers(many=True)
    comments = CommentsSerizlisers(many=True)


    class Meta:
        model = Task
        fields = '__all__'