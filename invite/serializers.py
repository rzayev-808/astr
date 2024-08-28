from rest_framework import serializers
from invite.models import *

class InviteSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = Invite
        exclude = ['acceptance']