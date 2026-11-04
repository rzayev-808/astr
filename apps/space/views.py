from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from rest_framework.generics import GenericAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from .serializers import SpaceSerializers, SpaceCreateSerializers, SpaceUpdateSerializers, SpaceMemberSerializers
from .models import Space
from rest_framework import status
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from invite.services import accept_pending_invites_for



class GetSpaceVirews(mixins.ListModelMixin, mixins.CreateModelMixin, GenericAPIView):

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SpaceCreateSerializers
        return SpaceSerializers

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Space.objects.none()
        # Həm özünün yaratdığı, həm də dəvətlə üzv olduğu space-lər
        user = self.request.user
        return Space.objects.filter(Q(creater_user=user) | Q(members=user)).distinct()

    def get(self, request, *args, **kwargs):
        # Dashboard açılanda ilk çağırılan ünvan budur. Adam artıq login idisə, login hadisəsi
        # olmur; ona görə bu email-ə gələn gözləyən dəvətlər burada da avtomatik qəbul olunur.
        accept_pending_invites_for(request.user)
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(creater_user=self.request.user)


class SpaceDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = SpaceUpdateSerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Space.objects.none()
        user = self.request.user
        if self.request.method in SAFE_METHODS:
            return Space.objects.filter(Q(creater_user=user) | Q(members=user)).distinct()
        return Space.objects.filter(creater_user=user)


class SpaceMemberAddView(GenericAPIView):
    serializer_class = SpaceMemberSerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Space.objects.none()
        return Space.objects.filter(creater_user=self.request.user)

    @swagger_auto_schema(operation_description="Space-ə bir üzv əlavə et (yalnız space yaradan). Body: {\"user\": <user_id>}")
    def post(self, request, pk):
        space = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            space.members.add(serializer.validated_data["user"])
            return Response({"success": "Member added to space"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SpaceMemberRemoveView(GenericAPIView):
    serializer_class = SpaceMemberSerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Space.objects.none()
        return Space.objects.filter(creater_user=self.request.user)

    @swagger_auto_schema(operation_description="Space-dən bir üzvü çıxar (yalnız space yaradan).")
    def delete(self, request, pk, user_id):
        space = get_object_or_404(self.get_queryset(), pk=pk)
        member = space.members.filter(pk=user_id).first()
        if member is None:
            return Response({"error": "User is not a member of this space"}, status=status.HTTP_404_NOT_FOUND)
        space.members.remove(member)
        return Response({"success": "Member removed from space"})
