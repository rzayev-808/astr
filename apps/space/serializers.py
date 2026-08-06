from rest_framework import serializers
from .models import Space
from cluster.serializers import ClusterSerializers
from squads.serializers import SquadSerializers
from pricing.serializers import PricingSerializers
from pricing.models import Pricing
from user.models import User
from user.serializers import UserGetAndDetailSerializers



class SpaceSerializers(serializers.ModelSerializer):

    cluster_space = ClusterSerializers(many=True)
    squad_space = SquadSerializers(many=True)
    pricing_plans = PricingSerializers()
    members = UserGetAndDetailSerializers(many=True)


    class Meta:
        model = Space
        fields = '__all__'


class SpaceCreateSerializers(serializers.ModelSerializer):

    class Meta:
        model = Space
        fields = '__all__'
        read_only_fields = ['creater_user']
        extra_kwargs = {'pricing_plans': {'required': False}}

    def create(self, validated_data):
        if not validated_data.get("pricing_plans"):
            validated_data["pricing_plans"] = Pricing.objects.filter(name="Free").last()
        return super().create(validated_data)


class SpaceUpdateSerializers(serializers.ModelSerializer):

    class Meta:
        model = Space
        fields = '__all__'
        read_only_fields = ['creater_user']


class SpaceMemberSerializers(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
