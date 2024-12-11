from django.db import models

# Create your models here.

class Invite(models.Model):
    email = models.CharField(max_length=200)
    role =  models.CharField(max_length=200)
    acceptance = models.BooleanField(default=False)
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.email