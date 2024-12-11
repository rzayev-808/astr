from django.shortcuts import render
from rest_framework.response import Response
from .serializers import InviteSerializers
from rest_framework.views import APIView
from rest_framework import status

# Create your views here.
class SendInvite(APIView):
    def get_serializer(self, *args, **kwargs):
        return InviteSerializers(*args, **kwargs)
    
    def post(self, request, format=None):
        serializers = InviteSerializers(data=request.data)
        if serializers.is_valid():
            item = serializers.save()
            print(serializers.data["email"])
            return Response(item.data,{"success":"Invite send to user"})
        return Response(item.errors, status=status.HTTP_400_BAD_REQUEST)