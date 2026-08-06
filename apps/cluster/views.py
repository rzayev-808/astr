from django.shortcuts import render
from django.db.models import Q
from rest_framework.generics import GenericAPIView,RetrieveUpdateAPIView,ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Cluster
from .serializers import ClusterMembersSerializers, ClusterCreateUpdateSerializers
from rest_framework import status
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.views import APIView


class ClusterViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Cluster.objects.all()

    def get_serializer_class(self):
        if getattr(self, 'action', None) in ["create", "update", "partial_update"]:
            return ClusterCreateUpdateSerializers
        return ClusterMembersSerializers

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Cluster.objects.none()
        if getattr(self, 'action', None) == "retrieve":
            return Cluster.objects.all()
        user = self.request.user
        return Cluster.objects.filter(
            Q(space__creater_user=user) | Q(space__members=user)
        ).distinct()
