from rest_framework import serializers
from .models import *

class ClusterSerializers(serializers.ModelSerializer):
    class Meta:
        model = Cluster
        exclude = ['space']