from django.test import TestCase
from rest_framework.test import APIClient

from cluster.models import Cluster
from pricing.models import Pricing
from space.models import Space
from user.models import User


def client_for(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


class ClusterAccessTests(TestCase):
    """Cluster-i yalnız space yaradanı və üzvləri görür; başqasına 404."""

    def setUp(self):
        Pricing.objects.create(name="Free")
        self.owner = User.objects.create(email="owner@test.az", fullname="Owner")
        self.member = User.objects.create(email="member@test.az", fullname="Member")
        self.stranger = User.objects.create(email="x@test.az", fullname="X")
        self.space = Space.objects.filter(creater_user=self.owner).first()
        self.space.members.add(self.member)
        self.cluster = Cluster.objects.create(name="C1", space=self.space)
        self.url = f"/cluster/api/{self.cluster.id}/"

    def test_anonymous_is_rejected(self):
        self.assertIn(APIClient().get(self.url).status_code, (401, 403))

    def test_owner_and_member_can_see(self):
        for u in (self.owner, self.member):
            self.assertEqual(client_for(u).get(self.url).status_code, 200, u.email)

    def test_stranger_gets_404(self):
        c = client_for(self.stranger)
        self.assertEqual(c.get(self.url).status_code, 404)
        self.assertEqual(c.get("/cluster/api/").json(), [])
        self.assertEqual(c.delete(self.url).status_code, 404)
        self.assertTrue(Cluster.objects.filter(pk=self.cluster.id).exists())

    def test_create_only_in_accessible_space(self):
        body = {"name": "New", "space": self.space.id}
        self.assertEqual(client_for(self.stranger).post("/cluster/api/", body, format="json").status_code, 403)
        self.assertEqual(client_for(self.member).post("/cluster/api/", body, format="json").status_code, 201)
