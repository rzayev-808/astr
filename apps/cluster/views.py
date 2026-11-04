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
from rest_framework.exceptions import PermissionDenied
from app.access import accessible_clusters, can_access_space


class ClusterViewset(viewsets.ModelViewSet):
    """Cluster-i yalnız space-in yaradanı/üzvü görür; girişi olmayana 404."""
    permission_classes = [IsAuthenticated]
    queryset = Cluster.objects.all()

    def get_serializer_class(self):
        if getattr(self, 'action', None) in ["create", "update", "partial_update"]:
            return ClusterCreateUpdateSerializers
        return ClusterMembersSerializers

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Cluster.objects.none()
        return accessible_clusters(self.request.user)

    def _check_space(self, serializer):
        space = serializer.validated_data.get("space")
        if space is not None and not can_access_space(self.request.user, space):
            raise PermissionDenied("You do not have access to this space")

    def perform_create(self, serializer):
        self._check_space(serializer)
        serializer.save()

    def perform_update(self, serializer):
        self._check_space(serializer)
        serializer.save()
