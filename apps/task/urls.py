from django.urls import path,include,re_path
from .views import *
from rest_framework import permissions

urlpatterns = [
    path('api/', TaskViewset.as_view({'get': 'list'}), name='task_get'),
]