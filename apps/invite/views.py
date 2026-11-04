from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from rest_framework.response import Response
from .serializers import InviteSerializers, InviteListSerializers, InvitePublicSerializer
from .models import Invite
from .services import accept_invite, InviteAcceptError
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, RetrieveDestroyAPIView
from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated, AllowAny
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

    @swagger_auto_schema(operation_description="Dəvət göndər. Dəvət olunana linkli məktub gedir; cavabda email_sent göstərir ki, məktub getdi ya yox.")
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


def _accept_response(invite, user, serializer):
    """Qəbul məntiqini çağırır, nəticəni HTTP cavabına çevirir (iki accept endpoint-i bunu paylaşır)."""
    try:
        accept_invite(invite, user)
    except InviteAcceptError as exc:
        return Response({"error": str(exc)}, status=exc.status)
    return Response({
        "success": "Invite accepted",
        "space": invite.space_id,
        "invite": serializer(invite).data,
    })


class AcceptInvite(GenericAPIView):
    serializer_class = InviteListSerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Invite.objects.all()

    @swagger_auto_schema(
        operation_description="Dəvəti id ilə qəbul et (yalnız dəvət olunan email-in sahibi). Space varsa, user avtomatik space üzvü olur. Cavabda space id var.",
        request_body=None,
    )
    def post(self, request, pk):
        invite = get_object_or_404(Invite, pk=pk)
        return _accept_response(invite, request.user, self.get_serializer_class())


class InviteByTokenView(GenericAPIView):
    """Məktubdakı linkin açdığı səhifə üçün. Login tələb etmir."""
    serializer_class = InvitePublicSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Invite.objects.all()

    @swagger_auto_schema(
        operation_description=(
            "Linkdəki kodla dəvət məlumatı (login lazım deyil): space, kim dəvət edib, email, status. "
            "user_exists=false → front-end register səhifəsinə (email hazır), "
            "user_exists=true → login səhifəsinə yönləndirir; "
            "is_current_user=true → login olan adam elə dəvət olunandır, birbaşa accept çağırmaq olar."
        ),
    )
    def get(self, request, token):
        invite = get_object_or_404(Invite, token=token)
        return Response(self.get_serializer(invite).data)


class AcceptInviteByTokenView(GenericAPIView):
    serializer_class = InvitePublicSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Invite.objects.all()

    @swagger_auto_schema(
        operation_description="Dəvəti linkdəki kodla qəbul et (login olan adamın email-i dəvətdəki ilə eyni olmalıdır). Cavabda space id var — front-end adamı həmin space-ə aparır.",
        request_body=None,
    )
    def post(self, request, token):
        invite = get_object_or_404(Invite, token=token)
        return _accept_response(invite, request.user, self.get_serializer_class())
