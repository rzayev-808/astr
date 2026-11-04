from django.urls import path,include,re_path
from .views import *
from rest_framework import permissions

urlpatterns = [
    path('api/', InviteView.as_view(), name='space_invite_send'),
    path('api/incoming/', IncomingInviteView.as_view(), name='invite_incoming'),
    path('api/by-token/<str:token>/', InviteByTokenView.as_view(), name='invite_by_token'),
    path('api/by-token/<str:token>/accept/', AcceptInviteByTokenView.as_view(), name='invite_accept_by_token'),
    path('api/<int:pk>/', InviteDetailView.as_view(), name='invite_detail_cancel'),
    path('api/<int:pk>/accept/', AcceptInvite.as_view(), name='invite_accept'),

]
