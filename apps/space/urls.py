from django.urls import path,include,re_path
from .views import *
from rest_framework import permissions

urlpatterns = [
    path('api/', GetSpaceVirews.as_view(), name='space_list_create'),
    path('api/<int:pk>/', SpaceDetailView.as_view(), name='space_detail'),
    path('api/<int:pk>/members/', SpaceMemberAddView.as_view(), name='space_member_add'),
    path('api/<int:pk>/members/<int:user_id>/', SpaceMemberRemoveView.as_view(), name='space_member_remove'),

]
