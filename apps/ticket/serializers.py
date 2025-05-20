from rest_framework import serializers
from task.serializers import TaskSerializers
from squads.serializers import SquadSerializers
from user.serializers import UserGetAndDetailSerializers
from .models import Ticket,Answer


class TicketViewSerializers(serializers.ModelSerializer):
    user = UserGetAndDetailSerializers(many=True)
    squad = SquadSerializers(many=True)
    task = TaskSerializers(many=True)
    class Meta:
        fields = '__all__'
    
    
class AnswerSerializers(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        
        
class TicketCreateEditSerializers(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'