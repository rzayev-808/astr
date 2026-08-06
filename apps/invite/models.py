from django.db import models
from space.models import Space
from user.models import User

# Create your models here.

class Invite(models.Model):
    email = models.CharField(max_length=200)
    role =  models.CharField(max_length=200)
    acceptance = models.BooleanField(default=False)
    create_date = models.DateTimeField(auto_now_add=True)
    space = models.ForeignKey(Space, on_delete=models.CASCADE, blank=True, null=True, related_name="invites")
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="sent_invites")

    def __str__(self) -> str:
        return self.email
