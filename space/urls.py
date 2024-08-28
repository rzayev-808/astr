from django.urls import path,include,re_path
from .views import *
from rest_framework import permissions

urlpatterns = [
    path('api/', GetSpaceVirews.as_view(), name='space_get'),
    path('api/<int:pk>/', SpaceDetailView.as_view())

]