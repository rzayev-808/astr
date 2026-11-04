from django.shortcuts import render
from django.db.models import Q
from rest_framework.generics import GenericAPIView,RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Squad
from .serializers import SquadSerializers, SquadCreateUpdateSerializers
from rest_framework import viewsets
from app.access import accessible_squads, can_access_space


class SquadViewset(viewsets.ModelViewSet):
    """Squad-ı yalnız girişi olan görür: space-in yaradanı/üzvü və ya squad üzvü.
    Girişi olmayana 404 (siyahıda da görünmür)."""
    permission_classes = [IsAuthenticated]
    queryset = Squad.objects.all()

    def get_serializer_class(self):
        if getattr(self, 'action', None) in ["create", "update", "partial_update"]:
            return SquadCreateUpdateSerializers
        return SquadSerializers

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Squad.objects.none()
        return accessible_squads(self.request.user)

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
