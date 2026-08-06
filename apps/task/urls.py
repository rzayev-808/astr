from django.urls import path,include,re_path
from .views import *
from rest_framework import permissions
from rest_framework import routers
router = routers.DefaultRouter()
router.register(r'create', TaskCreateViewset, basename='create')

urlpatterns = [
    path('api/', TaskViewset.as_view({'get': 'list'}), name='task_get'),
    path('api/<int:pk>/', TaskViewset.as_view({'get': 'retrieve','delete': 'destroy'}), name='task_detail'),
    path('mytask/',MyTaskViewset.as_view({'get': 'list'}),name='mytask'),
    # path('', include(router.urls)),
    path("api/create/",TaskCreateViewset.as_view({
    'post': 'create',
    }),name="create"),
    path("api/action/<int:pk>",TaskCreateViewset.as_view({
    # 'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
    }),name="update"),
    path("api/subtask/",SubTaskCreateViewset.as_view({
        'post': 'create',
    })),
     path("api/subtask/<int:pk>/",SubTaskCreateViewset.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    })),

    path("api/project/",ProjectViewset.as_view({
        'get': 'list',
        'post': 'create',
    }),name="project_list_create"),
    path("api/project/<int:pk>/",ProjectViewset.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }),name="project_detail"),

    path("api/add/comment/",AddCommentViewset.as_view({
        'post': 'create',
    })),

    path("api/add/file/",CreateFileViewset.as_view({
        'post': 'create',
    }))

]
