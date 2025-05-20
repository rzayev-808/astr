from django.urls import path,include,re_path
from .views import *
from rest_framework import permissions
from rest_framework import routers

urlpatterns = [

     path("api/",TicketViewset.as_view({
        'get': 'list',
        # 'put': 'update',
        # 'patch': 'partial_update',
        # 'delete': 'destroy'
    })),
     
    path("api/add/ticket/",TicketCreateViewset.as_view({
        'post': 'create',
    
    })),
     path("api/edit/ticket/<id>/",TicketCreateViewset.as_view({
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    
    })),
    
    path("api/create/answer/",AnsweCreateViewset.as_view({
        'post': 'create',
    })),
   
  
   
]
