from django.urls import path,include,re_path
from .views import *
from rest_framework import permissions

urlpatterns = [
    path('api/', ClusterViewset.as_view({'get': 'list', 'post': 'create'}), name='cluster_list_create'),
    path('api/<int:pk>/', ClusterViewset.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='cluster_detail'),

]
