from rest_framework import serializers
from invite.models import *

class InviteSerializers(serializers.ModelSerializer):

    class Meta:
        model = Invite
        exclude = ['acceptance']
        read_only_fields = ['invited_by']


class InviteListSerializers(serializers.ModelSerializer):

    class Meta:
        model = Invite
        fields = '__all__'
