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
from simple_history.models import HistoricalRecords
from rest_framework.exceptions import PermissionDenied
from app.access import accessible_tasks, can_access_squad, can_access_task

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

def _check_squad(request, serializer):
    """Task yalnız girişi olan squad-da yaradıla/ora köçürülə bilər."""
    squad = serializer.validated_data.get("squad")
    if squad is not None and not can_access_squad(request.user, squad):
        raise PermissionDenied("You do not have access to this squad")


def _check_task(request, serializer):
    """Şərh/fayl yalnız girişi olan task-a əlavə oluna bilər."""
    task = serializer.validated_data.get("task")
    if task is not None and not can_access_task(request.user, task):
        raise PermissionDenied("You do not have access to this task")


class TaskViewset(viewsets.ModelViewSet):  
    """Task-ları yalnız girişi olan görür/silir: squad-ın space yaradanı/üzvü, squad üzvü və ya task üzvü."""
    serializer_class = TaskSerializers
    queryset = Task.objects.all()
    filter_backends = [DjangoFilterBackend,]
    filterset_fields = ["squad_id","status","members__fullname"]
    filterset_class = TaskFilter

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Task.objects.none()
        return accessible_tasks(self.request.user)
   
   
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

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Task.objects.none()
        return accessible_tasks(self.request.user)

    def perform_create(self, serializer):
        _check_squad(self.request, serializer)
        serializer.save()

    def perform_update(self, serializer):
        _check_squad(self.request, serializer)
        serializer.save()
  
   
class SubTaskCreateViewset(viewsets.ModelViewSet):
    serializer_class = SubtaskSerializers
    queryset = SubTasks.objects.all()


class ProjectViewset(viewsets.ModelViewSet):
    serializer_class = ProjectSerializers
    queryset = Project.objects.all()
    
    
class AddCommentViewset(viewsets.ModelViewSet):
    serializer_class = CommentCreateSerializers
    queryset = Comment.objects.all()

    def perform_create(self, serializer):
        _check_task(self.request, serializer)
        serializer.save()
    
class HistoryViewset(viewsets.ModelViewSet):
    serializer_class = TaskHistorySerializer
    queryset = Task.history.all()
    
class CreateFileViewset(viewsets.ModelViewSet):
    serializer_class = FileTaksSerializers
    queryset = FileTaks.objects.all()

    def perform_create(self, serializer):
        _check_task(self.request, serializer)
        serializer.save()