from django.test import TestCase
from rest_framework.test import APIClient

from pricing.models import Pricing
from space.models import Space
from squads.models import Squad
from user.models import User


def client_for(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


class SquadAccessTests(TestCase):
    """Squad-ı yalnız girişi olan görür: space yaradanı, space üzvü, squad üzvü. Başqasına 404."""

    def setUp(self):
        Pricing.objects.create(name="Free")
        self.owner = User.objects.create(email="owner@test.az", fullname="Owner")
        self.member = User.objects.create(email="member@test.az", fullname="Member")
        self.squad_member = User.objects.create(email="sq@test.az", fullname="Sq")
        self.stranger = User.objects.create(email="x@test.az", fullname="X")
        self.space = Space.objects.filter(creater_user=self.owner).first()
        self.space.members.add(self.member)
        self.squad = Squad.objects.create(name="Alpha", space=self.space)
        self.squad.squad_members.add(self.squad_member)
        self.url = f"/squad/api/{self.squad.id}/"

    def test_anonymous_is_rejected(self):
        self.assertIn(APIClient().get(self.url).status_code, (401, 403))
        self.assertIn(APIClient().get("/squad/api/").status_code, (401, 403))

    def test_owner_space_member_and_squad_member_can_see(self):
        # dəvətlə gələn adam (space üzvü) öz space-inin squad-larını görür
        for u in (self.owner, self.member, self.squad_member):
            self.assertEqual(client_for(u).get(self.url).status_code, 200, u.email)
            self.assertIn(self.squad.id, [s["id"] for s in client_for(u).get("/squad/api/").json()])

    def test_stranger_gets_404_and_empty_list(self):
        # başqa space-in squad-ı görünmür
        c = client_for(self.stranger)
        self.assertEqual(c.get(self.url).status_code, 404)
        self.assertEqual(c.get("/squad/api/").json(), [])
        self.assertEqual(c.patch(self.url, {"name": "Hacked"}, format="json").status_code, 404)
        self.assertEqual(c.delete(self.url).status_code, 404)
        self.assertTrue(Squad.objects.filter(pk=self.squad.id, name="Alpha").exists())

    def test_create_only_in_accessible_space(self):
        body = {"name": "New", "space": self.space.id}
        self.assertEqual(client_for(self.stranger).post("/squad/api/", body, format="json").status_code, 403)
        self.assertEqual(client_for(self.member).post("/squad/api/", body, format="json").status_code, 201)

    def test_cannot_move_squad_to_foreign_space(self):
        foreign = Space.objects.filter(creater_user=self.stranger).first()
        r = client_for(self.owner).patch(self.url, {"space": foreign.id}, format="json")
        self.assertEqual(r.status_code, 403)


class SquadMembersAutoFillTests(TestCase):
    """Space üzvləri avtomatik squad üzvü olur (task-da üzv seçimi squad üzvlərindən gəlir)."""

    def setUp(self):
        Pricing.objects.create(name="Free")
        self.owner = User.objects.create(email="owner@test.az", fullname="Owner")
        self.member = User.objects.create(email="member@test.az", fullname="Member")
        self.space = Space.objects.filter(creater_user=self.owner).first()
        self.space.members.add(self.member)
        self.c = client_for(self.owner)

    def ids(self, squad):
        return set(squad.squad_members.values_list("id", flat=True))

    def test_new_squad_gets_all_space_members_including_creator(self):
        r = self.c.post("/squad/api/", {"name": "Alpha", "space": self.space.id}, format="json")
        self.assertEqual(r.status_code, 201, r.content)
        squad = Squad.objects.get(pk=r.json()["id"])
        self.assertEqual(self.ids(squad), {self.owner.id, self.member.id})
        self.assertEqual({m["id"] for m in r.json()["squad_members"]} if isinstance(r.json().get("squad_members", [None])[0], dict)
                         else set(r.json()["squad_members"]), {self.owner.id, self.member.id})

    def test_explicit_squad_members_on_create_are_respected(self):
        r = self.c.post("/squad/api/", {"name": "Beta", "space": self.space.id,
                                        "squad_members": [self.member.id]}, format="json")
        self.assertEqual(r.status_code, 201, r.content)
        self.assertEqual(self.ids(Squad.objects.get(pk=r.json()["id"])), {self.member.id})

    def test_accepted_invite_joins_existing_squads(self):
        from invite.models import Invite
        from invite.services import accept_invite
        squad = Squad.objects.create(name="Alpha", space=self.space)
        guest = User.objects.create(email="guest@test.az", fullname="Guest")
        self.assertNotIn(guest.id, self.ids(squad))
        accept_invite(Invite.objects.create(email="guest@test.az", role="dev", space=self.space,
                                            invited_by=self.owner), guest)
        self.assertIn(guest.id, self.ids(squad))

    def test_removing_from_space_removes_from_squads(self):
        squad = Squad.objects.create(name="Alpha", space=self.space)
        self.assertIn(self.member.id, self.ids(squad))
        r = self.c.delete(f"/space/api/{self.space.id}/members/{self.member.id}/")
        self.assertEqual(r.status_code, 200, r.content)
        self.assertNotIn(self.member.id, self.ids(squad))
        # artıq squad-a girişi yoxdur
        self.assertEqual(client_for(self.member).get(f"/squad/api/{squad.id}/").status_code, 404)

    def test_owner_can_still_trim_squad_members(self):
        squad = Squad.objects.create(name="Alpha", space=self.space)
        r = self.c.patch(f"/squad/api/{squad.id}/", {"squad_members": [self.owner.id]}, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(self.ids(squad), {self.owner.id})
