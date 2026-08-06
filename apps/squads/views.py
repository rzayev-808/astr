from django.shortcuts import render
from django.db.models import Q
from rest_framework.generics import GenericAPIView,RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Squad
from .serializers import SquadSerializers, SquadCreateUpdateSerializers
from rest_framework import viewsets


class SquadViewset(viewsets.ModelViewSet):
    queryset = Squad.objects.all()

    def get_serializer_class(self):
        if getattr(self, 'action', None) in ["create", "update", "partial_update"]:
            return SquadCreateUpdateSerializers
        return SquadSerializers

    def get_permissions(self):
        if getattr(self, 'action', None) == "retrieve":
            return []
        return [IsAuthenticated()]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Squad.objects.none()
        if getattr(self, 'action', None) == "retrieve":
            return Squad.objects.all()
        user = self.request.user
        return Squad.objects.filter(
            Q(space__creater_user=user) | Q(space__members=user) | Q(squad_members=user)
        ).distinct()
