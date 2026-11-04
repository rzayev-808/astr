from django.core import mail
from django.core.mail.backends.base import BaseEmailBackend
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from invite.emails import build_invite_link, send_invite_email
from invite.models import Invite
from pricing.models import Pricing
from space.models import Space
from user.models import User


class BrokenEmailBackend(BaseEmailBackend):
    """SMTP işləmir kimi davranan backend — xəta halını test etmək üçün."""

    def send_messages(self, email_messages):
        raise ConnectionError("smtp down")


@override_settings(INVITE_LINK_NEW_USER="https://app.test/signup?invite={token}",
                   INVITE_LINK_EXISTING_USER="https://app.test/logout?invite={token}",
                   SITE_NAME="Comestask")
class InviteEmailTests(TestCase):
    def setUp(self):
        Pricing.objects.create(name="Free")
        self.owner = User.objects.create(email="owner@test.az", fullname="Owner Adam")
        self.space = Space.objects.filter(creater_user=self.owner).first()
        self.c = APIClient()
        self.c.force_authenticate(user=self.owner)

    def test_post_invite_sends_email_with_link(self):
        r = self.c.post("/invite/api/", {"email": "new@test.az", "role": "dev",
                                         "space": self.space.id}, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        self.assertTrue(r.json()["email_sent"])
        self.assertNotIn("warning", r.json())
        inv_id = r.json()["invite"]["id"]

        self.assertEqual(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEqual(m.to, ["new@test.az"])
        self.assertEqual(m.subject, f"Owner Adam invited you to {self.space.space_name}")
        token = Invite.objects.get(pk=inv_id).token
        self.assertIn(f"https://app.test/signup?invite={token}", m.body)   # hesab yoxdur → qeydiyyat
        self.assertIn(self.space.space_name, m.body)
        self.assertIn("dev", m.body)

        html, mimetype = m.alternatives[0]
        self.assertEqual(mimetype, "text/html")
        self.assertIn(f"https://app.test/signup?invite={token}", html)
        self.assertIn("Owner Adam", html)

    def test_invite_without_space_uses_site_name(self):
        invite = Invite.objects.create(email="x@test.az", role="qa", invited_by=self.owner)
        self.assertTrue(send_invite_email(invite))
        self.assertEqual(mail.outbox[0].subject, "Owner Adam invited you to Comestask")
        self.assertIn(build_invite_link(invite), mail.outbox[0].body)

    @override_settings(EMAIL_BACKEND="invite.tests.BrokenEmailBackend")
    def test_email_failure_keeps_invite_and_warns(self):
        with self.assertLogs("invite.emails", level="ERROR"):
            r = self.c.post("/invite/api/", {"email": "new@test.az", "role": "dev",
                                             "space": self.space.id}, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        self.assertFalse(r.json()["email_sent"])
        self.assertIn("warning", r.json())
        self.assertTrue(Invite.objects.filter(email="new@test.az").exists())
        self.assertEqual(len(mail.outbox), 0)


class InviteTokenFlowTests(TestCase):
    """Linkdəki kodla axın: məlumat (login-siz) → qəbul (login ilə)."""

    def setUp(self):
        Pricing.objects.create(name="Free")
        self.owner = User.objects.create(email="owner@test.az", fullname="Owner Adam")
        self.space = Space.objects.filter(creater_user=self.owner).first()
        self.invite = Invite.objects.create(email="guest@test.az", role="dev",
                                            space=self.space, invited_by=self.owner)
        self.anon = APIClient()

    def test_token_is_generated_unique_and_hidden_from_api(self):
        other = Invite.objects.create(email="x@test.az", role="qa", space=self.space, invited_by=self.owner)
        self.assertGreaterEqual(len(self.invite.token), 40)
        self.assertNotEqual(self.invite.token, other.token)

        c = APIClient(); c.force_authenticate(user=self.owner)
        r = c.post("/invite/api/", {"email": "n@test.az", "role": "dev", "space": self.space.id}, format="json")
        self.assertNotIn("token", r.json()["invite"])
        r = c.get("/invite/api/")
        self.assertTrue(all("token" not in row for row in r.json()))

    @override_settings(INVITE_LINK_NEW_USER="https://app.test/signup?invite={token}",
                       INVITE_LINK_EXISTING_USER="https://app.test/logout?invite={token}")
    def test_email_link_depends_on_account_existence(self):
        # hesab yoxdur → qeydiyyat səhifəsi
        self.assertEqual(build_invite_link(self.invite), f"https://app.test/signup?invite={self.invite.token}")
        # hesab var → login səhifəsi
        User.objects.create(email="Guest@Test.az", fullname="Guest")
        self.assertEqual(build_invite_link(self.invite), f"https://app.test/logout?invite={self.invite.token}")
        send_invite_email(self.invite)
        self.assertIn(self.invite.token, mail.outbox[0].body)

    def test_public_info_without_login_user_missing(self):
        r = self.anon.get(f"/invite/api/by-token/{self.invite.token}/")
        self.assertEqual(r.status_code, 200, r.content)
        d = r.json()
        self.assertEqual(d["email"], "guest@test.az")
        self.assertEqual(d["space"], self.space.id)
        self.assertEqual(d["space_name"], self.space.space_name)
        self.assertEqual(d["invited_by_name"], "Owner Adam")
        self.assertEqual(d["status"], "pending")
        self.assertFalse(d["user_exists"])
        self.assertFalse(d["is_current_user"])

    def test_public_info_user_exists_and_is_current_user(self):
        guest = User.objects.create(email="Guest@Test.az", fullname="Guest")
        r = self.anon.get(f"/invite/api/by-token/{self.invite.token}/")
        self.assertTrue(r.json()["user_exists"])
        self.assertFalse(r.json()["is_current_user"])

        c = APIClient(); c.force_authenticate(user=guest)
        self.assertTrue(c.get(f"/invite/api/by-token/{self.invite.token}/").json()["is_current_user"])

    def test_public_info_unknown_token_404(self):
        self.assertEqual(self.anon.get("/invite/api/by-token/yoxdur/").status_code, 404)

    def test_accept_by_token_requires_login_and_matching_email(self):
        url = f"/invite/api/by-token/{self.invite.token}/accept/"
        self.assertIn(self.anon.post(url).status_code, (401, 403))

        stranger = User.objects.create(email="x@test.az", fullname="X")
        c = APIClient(); c.force_authenticate(user=stranger)
        self.assertEqual(c.post(url).status_code, 403)
        self.assertNotIn(stranger, self.space.members.all())

    def test_accept_by_token_adds_member_and_returns_space(self):
        guest = User.objects.create(email="guest@test.az", fullname="Guest")
        c = APIClient(); c.force_authenticate(user=guest)
        r = c.post(f"/invite/api/by-token/{self.invite.token}/accept/")
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(r.json()["space"], self.space.id)
        self.assertEqual(r.json()["invite"]["status"], "accepted")
        self.assertIn(guest, self.space.members.all())

        # ikinci dəfə olmaz
        r = c.post(f"/invite/api/by-token/{self.invite.token}/accept/")
        self.assertEqual(r.status_code, 400)

        # qəbuldan sonra space siyahısında görünür
        ids = [s["id"] for s in c.get("/space/api/").json()]
        self.assertIn(self.space.id, ids)

    def test_accept_by_id_still_works_and_returns_space(self):
        guest = User.objects.create(email="guest@test.az", fullname="Guest")
        c = APIClient(); c.force_authenticate(user=guest)
        r = c.post(f"/invite/api/{self.invite.id}/accept/")
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(r.json()["space"], self.space.id)


class IncomingInviteTests(TestCase):
    """GET /invite/api/incoming/ — yalnız mənim email-imə gələn dəvətlər."""

    def setUp(self):
        Pricing.objects.create(name="Free")
        self.owner = User.objects.create(email="owner@test.az", fullname="Owner")
        self.space = Space.objects.filter(creater_user=self.owner).first()
        self.me = User.objects.create(email="Me@Test.az", fullname="Me")
        self.mine = Invite.objects.create(email="me@test.az", role="dev", space=self.space, invited_by=self.owner)
        self.done = Invite.objects.create(email="me@test.az", role="qa", space=self.space,
                                          invited_by=self.owner, acceptance=True)
        Invite.objects.create(email="other@test.az", role="dev", space=self.space, invited_by=self.owner)
        self.c = APIClient(); self.c.force_authenticate(user=self.me)

    def test_lists_only_my_invites_without_token(self):
        r = self.c.get("/invite/api/incoming/")
        self.assertEqual(r.status_code, 200, r.content)
        rows = r.json()
        self.assertEqual({row["id"] for row in rows}, {self.mine.id, self.done.id})
        self.assertTrue(all("token" not in row for row in rows))
        row = next(x for x in rows if x["id"] == self.mine.id)
        self.assertEqual(row["space_name"], self.space.space_name)
        self.assertEqual(row["invited_by_name"], "Owner")
        self.assertEqual(row["status"], "pending")

    def test_filter_pending_only(self):
        rows = self.c.get("/invite/api/incoming/?acceptance=false").json()
        self.assertEqual([row["id"] for row in rows], [self.mine.id])

    def test_requires_login(self):
        self.assertIn(APIClient().get("/invite/api/incoming/").status_code, (401, 403))
