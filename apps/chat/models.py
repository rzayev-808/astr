from django.db import models
from user.models import User
from squads.models import Squad


class DirectMessage(models.Model):
    """İki istifadəçi arasında birbaşa (direct) mesaj. Mətn və/və ya fayl ola bilər."""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    text = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="chat_files", blank=True, null=True)
    is_read = models.BooleanField(default=False)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["create_date"]

    def __str__(self) -> str:
        return f"{self.sender.fullname} -> {self.receiver.fullname}"


class SquadMessage(models.Model):
    """Squad daxilindəki umumi chat mesajı. Mətn və/və ya fayl ola bilər."""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_squad_messages")
    squad = models.ForeignKey(Squad, on_delete=models.CASCADE, related_name="messages")
    text = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="chat_files", blank=True, null=True)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["create_date"]

    def __str__(self) -> str:
        return f"{self.sender.fullname} @ {self.squad.name}"
