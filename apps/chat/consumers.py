import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import DirectMessage, SquadMessage
from .serializers import DirectMessageSerializer, SquadMessageSerializer


class DirectChatConsumer(AsyncWebsocketConsumer):
    """İki istifadəçi arasındakı canlı direct chat.

    Qoşul: ws/chat/direct/<user_id>/?token=<jwt>
    Mesaj göndər (mətn): {"text": "salam"}
    Fayl mesajları REST POST ilə göndərilir və bura avtomatik yayımlanır.
    """

    async def connect(self):
        self.user = self.scope.get("user")
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        self.other_id = int(self.scope["url_route"]["kwargs"]["user_id"])
        a, b = sorted([self.user.id, self.other_id])
        self.group_name = f"dm_{a}_{b}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data or "{}")
        except json.JSONDecodeError:
            return
        text = (data.get("text") or "").strip()
        if not text:
            return

        message = await self._save(text)
        await self.channel_layer.group_send(
            self.group_name, {"type": "chat.message", "message": message}
        )

    @database_sync_to_async
    def _save(self, text):
        obj = DirectMessage.objects.create(
            sender=self.user, receiver_id=self.other_id, text=text
        )
        return DirectMessageSerializer(obj).data

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event["message"], default=str))


class SquadChatConsumer(AsyncWebsocketConsumer):
    """Squad-ın canlı umumi chat-i.

    Qoşul: ws/chat/squad/<squad_id>/?token=<jwt>
    Mesaj göndər (mətn): {"text": "hamıya salam"}
    Fayl mesajları REST POST ilə göndərilir və bura avtomatik yayımlanır.
    """

    async def connect(self):
        self.user = self.scope.get("user")
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        self.squad_id = int(self.scope["url_route"]["kwargs"]["squad_id"])
        if not await self._can_access():
            # Bu squad-a girişi yoxdur (nə space yaradanı/üzvü, nə squad üzvü)
            await self.close(code=4003)
            return
        self.group_name = f"squad_{self.squad_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    @database_sync_to_async
    def _can_access(self):
        from app.access import accessible_squads
        return accessible_squads(self.user).filter(pk=self.squad_id).exists()

    async def disconnect(self, code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data or "{}")
        except json.JSONDecodeError:
            return
        text = (data.get("text") or "").strip()
        if not text:
            return

        message = await self._save(text)
        await self.channel_layer.group_send(
            self.group_name, {"type": "chat.message", "message": message}
        )

    @database_sync_to_async
    def _save(self, text):
        obj = SquadMessage.objects.create(
            sender=self.user, squad_id=self.squad_id, text=text
        )
        return SquadMessageSerializer(obj).data

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event["message"], default=str))
