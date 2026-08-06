from django.urls import path,include,re_path
from .views import *
from rest_framework import permissions

urlpatterns = [
    path('api/', SquadViewset.as_view({'get': 'list', 'post': 'create'}), name='squad_list_create'),
    path('api/<int:pk>/', SquadViewset.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='squad_detail'),

]
