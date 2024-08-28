from django.shortcuts import render
from rest_framework.generics import GenericAPIView,RetrieveUpdateAPIView,ListAPIView
from rest_framework.response import Response
from .models import Cluster
from .serializers import ClusterMembersSerializers
from rest_framework import status
from rest_framework import mixins
from rest_framework.views import APIView


class ClusterMembers(ListAPIView):
    serializer_class = ClusterMembersSerializers

    def get_queryset(self):
        return Cluster.objects.filter(space__creater_user=self.request.user)
