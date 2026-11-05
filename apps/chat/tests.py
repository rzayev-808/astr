from channels.layers import InMemoryChannelLayer
from django.conf import settings
from django.test import SimpleTestCase, TestCase, override_settings
from rest_framework.test import APIClient

from chat.models import DirectMessage, SquadMessage
from pricing.models import Pricing
from space.models import Space
from squads.models import Squad
from user.models import User

IN_MEMORY_LAYER = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}


def client_for(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


@override_settings(CHANNEL_LAYERS=IN_MEMORY_LAYER)
class SquadChatAccessTests(TestCase):
    """Squad chat-ini yalnız girişi olan oxuyur və ora yazır."""

    def setUp(self):
        Pricing.objects.create(name="Free")
        self.owner = User.objects.create(email="owner@test.az", fullname="Owner")
        self.squad_member = User.objects.create(email="sq@test.az", fullname="Sq")
        self.stranger = User.objects.create(email="x@test.az", fullname="X")
        self.space_member = User.objects.create(email="member@test.az", fullname="Member")
        self.space = Space.objects.filter(creater_user=self.owner).first()
        self.space.members.add(self.space_member)
        self.squad = Squad.objects.create(name="Alpha", space=self.space)
        self.squad.squad_members.add(self.squad_member)
        SquadMessage.objects.create(sender=self.owner, squad=self.squad, text="salam")
        self.url = f"/chat/api/squad/{self.squad.id}/"

    def test_member_can_read_and_post(self):
        c = client_for(self.squad_member)
        self.assertEqual(len(c.get(self.url).json()), 1)
        self.assertEqual(c.post(self.url, {"text": "hey"}).status_code, 201)
        self.assertEqual(SquadMessage.objects.filter(squad=self.squad).count(), 2)

    def test_stranger_cannot_read_or_post(self):
        c = client_for(self.stranger)
        self.assertEqual(c.get(self.url).json(), [])
        self.assertEqual(c.post(self.url, {"text": "hey"}).status_code, 404)
        self.assertEqual(SquadMessage.objects.filter(squad=self.squad).count(), 1)

    def test_owner_and_space_member_can_read(self):
        for u in (self.owner, self.space_member):
            self.assertEqual(len(client_for(u).get(self.url).json()), 1, u.email)

    def test_anonymous_is_rejected(self):
        self.assertIn(APIClient().get(self.url).status_code, (401, 403))


class BrokenChannelLayer(InMemoryChannelLayer):
    """Redis işləmir kimi davranan canlı yayım qatı — xəta halını test etmək üçün."""

    async def group_send(self, group, message):
        raise ConnectionError("redis down")


BROKEN_LAYER = {"default": {"BACKEND": "chat.tests.BrokenChannelLayer"}}


@override_settings(CHANNEL_LAYERS=BROKEN_LAYER)
class ChatWithoutLiveDeliveryTests(TestCase):
    """Canlı yayım (Redis) işləməsə də mesaj yazılır və sorğu 500 vermir."""

    def setUp(self):
        Pricing.objects.create(name="Free")
        self.owner = User.objects.create(email="owner@test.az", fullname="Owner")
        self.other = User.objects.create(email="other@test.az", fullname="Other")
        self.space = Space.objects.filter(creater_user=self.owner).first()
        self.squad = Squad.objects.create(name="Alpha", space=self.space)

    def test_squad_message_is_saved_and_reason_is_logged(self):
        with self.assertLogs("chat.broadcast", level="ERROR") as logs:
            r = client_for(self.owner).post(f"/chat/api/squad/{self.squad.id}/", {"text": "salam"})
        self.assertEqual(r.status_code, 201, r.content)
        self.assertEqual(SquadMessage.objects.filter(squad=self.squad, text="salam").count(), 1)
        self.assertIn("redis down", logs.output[0])

    def test_direct_message_is_saved(self):
        with self.assertLogs("chat.broadcast", level="ERROR"):
            r = client_for(self.owner).post(f"/chat/api/direct/{self.other.id}/", {"text": "salam"})
        self.assertEqual(r.status_code, 201, r.content)
        self.assertEqual(DirectMessage.objects.filter(sender=self.owner, receiver=self.other).count(), 1)



class LiveChatSettingsTests(SimpleTestCase):
    """Redis-dən cavab gözləmə həddi chat-ın mesaj gözləmə müddətindən böyük olmalıdır.
    Bərabər olanda boş qalan WebSocket bağlantısı bir neçə saniyəyə qırılır."""

    def test_redis_read_timeout_is_longer_than_message_wait(self):
        from channels_redis.core import RedisChannelLayer

        host = settings.CHANNEL_LAYERS["default"]["CONFIG"]["hosts"][0]
        self.assertGreater(host["socket_timeout"], RedisChannelLayer.brpop_timeout)
