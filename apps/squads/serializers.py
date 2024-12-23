from rest_framework import serializers
from .models import *
from user.serializers import UserGetAndDetailSerializers

class SquadSerializers(serializers.ModelSerializer):
    squad_members = UserGetAndDetailSerializers(many=True)
    class Meta:
        model = Squad
        exclude = ['space']

