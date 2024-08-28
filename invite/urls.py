from django.urls import path,include,re_path
from .views import *
from rest_framework import permissions

urlpatterns = [
    path('api/', SendInvite.as_view(), name='space_invite_send'),

]