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
            data = tasks.filter(squad_id=squad_id)

        if status:
            data = tasks.filter(status=status)
        serializer = TaskSerializers(data, many=True)
        return Response(serializer.data)
   
   