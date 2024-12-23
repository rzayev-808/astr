from django.urls import path,include,re_path
from .views import *
from rest_framework import permissions

urlpatterns = [
    path('api/<int:pk>/', SquadetailView.as_view({'get': 'retrieve'}), name='squad_get'),

]