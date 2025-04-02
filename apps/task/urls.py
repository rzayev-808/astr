from django.urls import path,include,re_path
from .views import *
from rest_framework import permissions
from rest_framework import routers
router = routers.DefaultRouter()
router.register(r'create', TaskCreateViewset, basename='create')

urlpatterns = [
    path('api/', TaskViewset.as_view({'get': 'list'}), name='task_get'),
    path('api/<pk>/', TaskViewset.as_view({'get': 'retrieve'}), name='task_detail'),
    path('mytask/',MyTaskViewset.as_view({'get': 'list'}),name='mytask'),
    # path('', include(router.urls)),
    path("api/create/",TaskCreateViewset.as_view({
    'post': 'create',
    }),name="create"),
    path("api/action/<pk>",TaskCreateViewset.as_view({
    # 'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
    }),name="update")
   
]
