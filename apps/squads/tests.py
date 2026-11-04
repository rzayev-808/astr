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

    def test_owner_and_squad_member_can_see(self):
        for u in (self.owner, self.squad_member):
            self.assertEqual(client_for(u).get(self.url).status_code, 200, u.email)
            self.assertIn(self.squad.id, [s["id"] for s in client_for(u).get("/squad/api/").json()])

    def test_space_member_outside_squad_and_stranger_get_404(self):
        # adi space üzvü yalnız öz squad-larını görür; bu squad-da deyil → görmür
        for u in (self.member, self.stranger):
            c = client_for(u)
            self.assertEqual(c.get(self.url).status_code, 404, u.email)
            self.assertEqual(c.get("/squad/api/").json(), [], u.email)
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
