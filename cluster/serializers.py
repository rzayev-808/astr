from rest_framework import serializers
from .models import *
from space.models import Space

class ClusterSerializers(serializers.ModelSerializer):
    class Meta:
        model = Cluster
        exclude = ['space']


class ClusterMembersSerializers(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()

    def get_members(self, obj):
        
        res = Space.objects.filter(cluster_space__id__in=[obj.id])
        members = [[{"fullname":q.fullname,"id":q.id,"role":q.position} for q in x.members.all()] for x in res]
        return members
    
    class Meta:
        model = Cluster
        fields = '__all__'

