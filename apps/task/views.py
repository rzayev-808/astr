from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from .models import *
from .serializers import *
from rest_framework.response import Response
from django.db.models import Q

class TaskViews(APIView):
    def get(self, request):
        tasks = Task.objects.all()
        squad_id = request.GET["squad_id"]
        status = request.GET.get("status")
        if squad_id:
            tasks.filter(squad_id=squad_id)
        if status:
            tasks.filter(status=status)
        serializer = TaskSerializers(tasks, many=True)
        return Response(serializer.data)
    # def get_serializer(self, *args, **kwargs):
    #     return TaskSerializers(*args, **kwargs)
    
    # def post(self, request, format=None):
    #     serializers = TaskSerializers(data=request.data)
    #     if serializers.is_valid():
    #         item = serializers.save()
    #         print(serializers.data["email"])
    #         return Response({"success":"Invite send to user"})