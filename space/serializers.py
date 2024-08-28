from rest_framework import serializers
from .models import Space
from cluster.serializers import ClusterSerializers
from squads.serializers import SquadSerializers
from pricing.serializers import PricingSerializers
from invite.models import *

class InviteSerializers(serializers.Serializer):
    
    class Meta:
        model = Invite
        fields = '__all__'



class SpaceSerializers(serializers.ModelSerializer):

    cluster_space = ClusterSerializers(many=True)
    squad_space = SquadSerializers(many=True)
    pricing_plans = PricingSerializers()

    class Meta:
        model = Space
        fields = '__all__'

   

class SpaceUpdateSerializers(serializers.ModelSerializer):

    

    class Meta:
        model = Space
        fields = '__all__'