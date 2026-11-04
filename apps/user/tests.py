from django.core import mail
from django.core.mail.backends.base import BaseEmailBackend
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from pricing.models import Pricing
from user.emails import build_password_reset_link
from user.models import PasswordReset, User


class BrokenEmailBackend(BaseEmailBackend):
    """SMTP işləmir kimi davranan backend — xəta halını test etmək üçün."""

    def send_messages(self, email_messages):
        raise ConnectionError("smtp down")


@override_settings(PASSWORD_RESET_LINK="https://app.test/reset-password/{token}", SITE_NAME="Comestask")
class PasswordResetEmailTests(TestCase):
    REQUEST_URL = "/auth/api/reset_password/request/"

    def setUp(self):
        Pricing.objects.create(name="Free")
        self.user = User.objects.create_user(email="u@test.az", fullname="Ulvi", password="OldPass1!")
        self.c = APIClient()

    def test_request_sends_email_with_token_link(self):
        r = self.c.post(self.REQUEST_URL, {"email": "u@test.az"}, format="json")
        self.assertEqual(r.status_code, 200, r.content)

        reset = PasswordReset.objects.get(email="u@test.az")
        self.assertEqual(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEqual(m.to, ["u@test.az"])
        self.assertEqual(m.subject, "Reset your Comestask password")
        self.assertIn(build_password_reset_link(reset.token), m.body)
        self.assertIn("Ulvi", m.body)
        html, mimetype = m.alternatives[0]
        self.assertEqual(mimetype, "text/html")
        self.assertIn(f"https://app.test/reset-password/{reset.token}", html)

    def test_request_is_case_insensitive(self):
        r = self.c.post(self.REQUEST_URL, {"email": "U@TEST.AZ"}, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(mail.outbox[0].to, ["u@test.az"])

    def test_unknown_email_returns_404_and_no_mail(self):
        r = self.c.post(self.REQUEST_URL, {"email": "nobody@test.az"}, format="json")
        self.assertEqual(r.status_code, 404)
        self.assertEqual(len(mail.outbox), 0)

    def test_missing_or_invalid_email_returns_400(self):
        self.assertEqual(self.c.post(self.REQUEST_URL, {}, format="json").status_code, 400)
        self.assertEqual(self.c.post(self.REQUEST_URL, {"email": "not-an-email"}, format="json").status_code, 400)
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(EMAIL_BACKEND="user.tests.BrokenEmailBackend")
    def test_email_failure_returns_503(self):
        with self.assertLogs("user.emails", level="ERROR"):
            r = self.c.post(self.REQUEST_URL, {"email": "u@test.az"}, format="json")
        self.assertEqual(r.status_code, 503, r.content)
        self.assertEqual(len(mail.outbox), 0)

    def test_full_flow_token_from_email_changes_password(self):
        self.c.post(self.REQUEST_URL, {"email": "u@test.az"}, format="json")
        token = PasswordReset.objects.get(email="u@test.az").token
        self.assertIn(token, mail.outbox[0].body)

        r = self.c.post(f"/auth/api/reset_password/{token}/",
                        {"new_password": "NewPass1!", "confirm_password": "NewPass1!"}, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPass1!"))
        self.assertFalse(PasswordReset.objects.filter(token=token).exists())


class RegisterWithInviteTests(TestCase):
    """Dəvət linkindən qeydiyyat: hesab yaranır, dəvət qəbul olunur, adam space-ə düşür."""
    URL = "/auth/api/register/"
    BODY = {"email": "guest@test.az", "fullname": "Guest", "password": "StrongPass1!", "password2": "StrongPass1!"}

    def setUp(self):
        from invite.models import Invite
        from space.models import Space
        Pricing.objects.create(name="Free")
        self.owner = User.objects.create(email="owner@test.az", fullname="Owner")
        self.space = Space.objects.filter(creater_user=self.owner).first()
        self.invite = Invite.objects.create(email="guest@test.az", role="dev",
                                            space=self.space, invited_by=self.owner)
        self.c = APIClient()

    def test_register_without_token_still_works(self):
        r = self.c.post(self.URL, self.BODY, format="json")
        self.assertEqual(r.status_code, 201, r.content)
        self.assertIsNone(r.json()["space"])
        self.assertTrue(User.objects.filter(email="guest@test.az").exists())

    def test_register_with_token_accepts_invite_and_returns_space(self):
        r = self.c.post(self.URL, {**self.BODY, "invite_token": self.invite.token}, format="json")
        self.assertEqual(r.status_code, 201, r.content)
        self.assertEqual(r.json()["space"], self.space.id)
        guest = User.objects.get(email="guest@test.az")
        self.assertIn(guest, self.space.members.all())
        self.invite.refresh_from_db()
        self.assertTrue(self.invite.acceptance)

        # girəndən sonra space siyahısında görür
        c = APIClient(); c.force_authenticate(user=guest)
        self.assertIn(self.space.id, [s["id"] for s in c.get("/space/api/").json()])

    def test_register_with_token_but_different_email_rejected(self):
        body = {**self.BODY, "email": "other@test.az", "invite_token": self.invite.token}
        r = self.c.post(self.URL, body, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("invite_token", r.json())
        self.assertFalse(User.objects.filter(email="other@test.az").exists())

    def test_register_with_bad_or_used_token_rejected(self):
        r = self.c.post(self.URL, {**self.BODY, "invite_token": "yoxdur"}, format="json")
        self.assertEqual(r.status_code, 400)
        self.invite.acceptance = True; self.invite.save()
        r = self.c.post(self.URL, {**self.BODY, "invite_token": self.invite.token}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertFalse(User.objects.filter(email="guest@test.az").exists())
