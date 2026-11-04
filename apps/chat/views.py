from rest_framework.generics import GenericAPIView
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from django.shortcuts import get_object_or_404

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import DirectMessage, SquadMessage
from .serializers import DirectMessageSerializer, SquadMessageSerializer
from .broadcast import broadcast_direct, broadcast_squad
from user.models import User
from squads.models import Squad
from app.access import accessible_squads

# Mesaj göndərmə üçün form sahələri (mətn və/və ya fayl).
# IN_FORM + TYPE_FILE Swagger-də fayl seçici (multipart/form-data) göstərir.
TEXT_PARAM = openapi.Parameter(
    "text", openapi.IN_FORM, type=openapi.TYPE_STRING, required=False,
    description="Mesaj mətni (fayl yoxdursa mütləqdir)",
)
FILE_PARAM = openapi.Parameter(
    "file", openapi.IN_FORM, type=openapi.TYPE_FILE, required=False,
    description="Göndərilən fayl (mətn yoxdursa mütləqdir)",
)


class InboxView(mixins.ListModelMixin, GenericAPIView):
    """Mənim iştirak etdiyim bütün direct mesajlar (göndərdiyim + aldığım)."""
    serializer_class = DirectMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        me = self.request.user
        return DirectMessage.objects.filter(Q(sender=me) | Q(receiver=me))

    @swagger_auto_schema(
        operation_summary="Inbox — bütün direct söhbətlərim",
        operation_description="Cari istifadəçinin göndərdiyi və aldığı bütün direct mesajları qaytarır.",
        tags=["Chat - Direct"],
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DirectMessageView(mixins.ListModelMixin, mixins.CreateModelMixin, GenericAPIView):
    """user_id ilə aramdakı söhbət: GET — mesajları gətir, POST — yeni mesaj göndər."""
    serializer_class = DirectMessageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        me = self.request.user
        other_id = self.kwargs["user_id"]
        return DirectMessage.objects.filter(
            Q(sender=me, receiver_id=other_id) | Q(sender_id=other_id, receiver=me)
        )

    @swagger_auto_schema(
        operation_summary="Söhbəti aç — user_id ilə mesaj tarixçəsi",
        operation_description=(
            "Cari istifadəçi ilə <b>user_id</b> arasındakı bütün mesajları qaytarır. "
            "Qarşı tərəfdən gələn oxunmamış mesajlar avtomatik 'oxundu' (is_read=true) kimi işarələnir."
        ),
        tags=["Chat - Direct"],
    )
    def get(self, request, *args, **kwargs):
        # Qarşı tərəfdən gələn oxunmamış mesajları "oxundu" kimi işarələ
        DirectMessage.objects.filter(
            sender_id=self.kwargs["user_id"], receiver=request.user, is_read=False
        ).update(is_read=True)
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Direct mesaj göndər (mətn və/və ya fayl)",
        operation_description=(
            "<b>user_id</b>-ə yeni direct mesaj göndərir. <b>text</b>, <b>file</b> "
            "və ya hər ikisi göndərilə bilər (ən azı biri olmalıdır). "
            "Fayl göndərmək üçün <code>multipart/form-data</code> istifadə edin. "
            "Mesaj həm bazaya yazılır, həm də qoşulu olan tərəfə WebSocket ilə canlı çatdırılır."
        ),
        manual_parameters=[TEXT_PARAM, FILE_PARAM],
        responses={201: DirectMessageSerializer},
        tags=["Chat - Direct"],
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        receiver = get_object_or_404(User, pk=self.kwargs["user_id"])
        obj = serializer.save(sender=self.request.user, receiver=receiver)
        data = DirectMessageSerializer(obj, context={"request": self.request}).data
        broadcast_direct(data, self.request.user.id, receiver.id)


class SquadMessageView(mixins.ListModelMixin, mixins.CreateModelMixin, GenericAPIView):
    """Squad-ın umumi chat-i: GET — mesajları gətir, POST — yeni mesaj göndər."""
    serializer_class = SquadMessageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        # Yalnız girişi olan squad-ın mesajları (space yaradanı/üzvü və ya squad üzvü)
        return SquadMessage.objects.filter(
            squad_id=self.kwargs["squad_id"],
            squad__in=accessible_squads(self.request.user),
        )

    @swagger_auto_schema(
        operation_summary="Squad umumi chat — mesajları gətir",
        operation_description="<b>squad_id</b>-li squad-ın umumi chat-indəki bütün mesajları qaytarır.",
        tags=["Chat - Squad"],
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Squad umumi chat-ə mesaj göndər (mətn və/və ya fayl)",
        operation_description=(
            "<b>squad_id</b>-li squad-ın umumi chat-inə mesaj göndərir. <b>text</b>, <b>file</b> "
            "və ya hər ikisi (ən azı biri olmalıdır). Fayl üçün <code>multipart/form-data</code>. "
            "Mesaj squad-a qoşulu olan bütün üzvlərə WebSocket ilə canlı çatdırılır."
        ),
        manual_parameters=[TEXT_PARAM, FILE_PARAM],
        responses={201: SquadMessageSerializer},
        tags=["Chat - Squad"],
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        squad = get_object_or_404(accessible_squads(self.request.user), pk=self.kwargs["squad_id"])
        obj = serializer.save(sender=self.request.user, squad=squad)
        data = SquadMessageSerializer(obj, context={"request": self.request}).data
        broadcast_squad(data, squad.id)
