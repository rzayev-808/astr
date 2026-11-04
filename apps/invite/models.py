import secrets

from django.db import models
from space.models import Space
from user.models import User

# Create your models here.


def generate_invite_token():
    """Məktubdakı linkdə gedən təsadüfi gizli kod (43 simvol)."""
    return secrets.token_urlsafe(32)


class Invite(models.Model):
    email = models.CharField(max_length=200)
    role =  models.CharField(max_length=200)
    acceptance = models.BooleanField(default=False)
    create_date = models.DateTimeField(auto_now_add=True)
    space = models.ForeignKey(Space, on_delete=models.CASCADE, blank=True, null=True, related_name="invites")
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="sent_invites")
    # Linkdəki gizli kod. Yalnız məktubu alan bilir; API cavablarında göstərilmir.
    token = models.CharField(max_length=64, unique=True, default=generate_invite_token, editable=False)

    def __str__(self) -> str:
        return self.email

    @property
    def status(self):
        return "accepted" if self.acceptance else "pending"
