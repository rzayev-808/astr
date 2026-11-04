from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from rest_framework.response import Response
from .serializers import InviteSerializers, InviteListSerializers
from .models import Invite
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, RetrieveDestroyAPIView
from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from .emails import send_invite_email

# Create your views here.
class InviteView(mixins.ListModelMixin, GenericAPIView):
    permission_classes = [IsAuthenticated]
    filterset_fields = ['acceptance', 'space']

    def get_serializer_class(self):
        if self.request.method == "POST":
            return InviteSerializers
        return InviteListSerializers

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Invite.objects.none()
        user = self.request.user
        return Invite.objects.filter(
            Q(invited_by=user) | Q(space__creater_user=user)
        ).distinct()

    @swagger_auto_schema(operation_description="Mənim göndərdiyim / mənim space-lərimə aid dəvətlərin siyahısı. ?acceptance=false ilə pending-ləri filtrlə.")
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Dəvət göndər.")
    def post(self, request, *args, **kwargs):
        serializers = InviteSerializers(data=request.data)
        if serializers.is_valid():
            invite = serializers.save(invited_by=request.user)
            email_sent = send_invite_email(invite)
            payload = {"success": "Invite send to user", "email_sent": email_sent, "invite": serializers.data}
            if not email_sent:
                payload["warning"] = "Invite saved, but the email could not be sent"
            return Response(payload)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


class InviteDetailView(RetrieveDestroyAPIView):
    serializer_class = InviteListSerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Invite.objects.none()
        user = self.request.user
        return Invite.objects.filter(
            Q(invited_by=user) | Q(space__creater_user=user)
        ).distinct()


class AcceptInvite(GenericAPIView):
    serializer_class = InviteListSerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Invite.objects.all()

    @swagger_auto_schema(
        operation_description="Dəvəti qəbul et (yalnız dəvət olunan email-in sahibi). Space varsa, user avtomatik space üzvü olur.",
        request_body=None,
    )
    def post(self, request, pk):
        invite = get_object_or_404(Invite, pk=pk)
        if invite.email.lower() != request.user.email.lower():
            return Response({"error": "This invite was not sent to your email"}, status=status.HTTP_403_FORBIDDEN)
        if invite.acceptance:
            return Response({"error": "Invite already accepted"}, status=status.HTTP_400_BAD_REQUEST)
        invite.acceptance = True
        invite.save()
        if invite.space:
            invite.space.members.add(request.user)
        return Response({"success": "Invite accepted", "invite": self.get_serializer(invite).data})
