from rest_framework import serializers
from .models import *

class SquadSerializers(serializers.ModelSerializer):
    class Meta:
        model = Squad
        exclude = ['space']