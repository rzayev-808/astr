from django.test import TestCase
from rest_framework.test import APIClient

from pricing.models import Pricing
from space.models import Space
from user.models import User


class SpaceListVisibilityTests(TestCase):
    """Space siyahısı: özünün yaratdığı + üzv olduğu space-lər, başqasınınkı yox."""

    def setUp(self):
        Pricing.objects.create(name="Free")
        self.owner = User.objects.create(email="owner@test.az", fullname="Owner")
        self.member = User.objects.create(email="member@test.az", fullname="Member")
        self.stranger = User.objects.create(email="x@test.az", fullname="X")
        self.space = Space.objects.filter(creater_user=self.owner).first()
        self.space.members.add(self.member)

    def ids_for(self, user):
        c = APIClient(); c.force_authenticate(user=user)
        return {s["id"] for s in c.get("/space/api/").json()}

    def test_member_sees_space_in_list(self):
        own = Space.objects.get(creater_user=self.member).id
        self.assertEqual(self.ids_for(self.member), {own, self.space.id})

    def test_owner_and_stranger(self):
        self.assertEqual(self.ids_for(self.owner), {self.space.id})
        self.assertEqual(self.ids_for(self.stranger), {Space.objects.get(creater_user=self.stranger).id})

    def test_member_can_read_but_not_edit_or_delete(self):
        c = APIClient(); c.force_authenticate(user=self.member)
        self.assertEqual(c.get(f"/space/api/{self.space.id}/").status_code, 200)
        self.assertEqual(c.patch(f"/space/api/{self.space.id}/", {"company": "X"}, format="json").status_code, 404)
        self.assertEqual(c.delete(f"/space/api/{self.space.id}/").status_code, 404)


class SpaceAnonymousTests(TestCase):
    def test_anonymous_is_rejected_everywhere(self):
        for url in ("/space/api/", "/space/api/1/", "/auth/api/user/", "/task/api/project/"):
            self.assertIn(APIClient().get(url).status_code, (401, 403), url)
