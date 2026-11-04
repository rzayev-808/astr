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


@override_settings(INVITE_LINK="https://app.test/invite/{id}", SITE_NAME="Comestask")
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
        self.assertIn(f"https://app.test/invite/{inv_id}", m.body)
        self.assertIn(self.space.space_name, m.body)
        self.assertIn("dev", m.body)

        html, mimetype = m.alternatives[0]
        self.assertEqual(mimetype, "text/html")
        self.assertIn(f"https://app.test/invite/{inv_id}", html)
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
