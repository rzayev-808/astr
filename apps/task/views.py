from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from .models import *
from .serializers import *
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from django_filters import rest_framework as filters

# class TaskViews(APIView):
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter]
#     filterset_fields = ["status",]
#     def get(self, request):
#         tasks = Task.objects.all()
#         squad_id = request.GET["squad_id"]
#         # status = request.GET.get("status")
#         date_to = request.GET.get("date_to")
#         date_end = request.GET.get("date_end")
#         if squad_id:
#             data = tasks.filter(squad_id=squad_id)

#         # if status:
#         #     data = tasks.filter(status=status)
#         # if date_to
#         serializer = TaskSerializers(data, many=True)
#         return Response(serializer.data)
   
   
class TaskFilter(filters.FilterSet):
    create_date = filters.DateFromToRangeFilter()

    class Meta:
        model = Task
        fields = ['squad_id',"importance","topics", 'status', 'members__fullname', 'create_date',"deadline",]

class TaskViewset(viewsets.ModelViewSet):  
    serializer_class = TaskSerializers
    queryset = Task.objects.all()
    filter_backends = [DjangoFilterBackend,]
    filterset_fields = ["squad_id","status","members__fullname"]
    filterset_class = TaskFilter
   
   
class MyTaskViewset(viewsets.ModelViewSet):  
    serializer_class = TaskSerializers
    filter_backends = [DjangoFilterBackend,]
    filterset_fields = ["squad_id","status","members__fullname"]
    filterset_class = TaskFilter
    
    def get_queryset(self):
        return Task.objects.filter(members__in=[self.request.user.id])

   
class TaskCreateViewset(viewsets.ModelViewSet):  
    serializer_class = TaskCreateSerializers
    queryset = Task.objects.all()
  
   
