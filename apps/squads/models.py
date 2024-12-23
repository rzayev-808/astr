from django.db import models
from space.models import Space
from user.models import User

class Squad(models.Model):
    name = models.CharField(max_length=200)
    create_date = models.DateTimeField(auto_now_add=True)
    space = models.ForeignKey(Space,on_delete=models.CASCADE,related_name="squad_space")
    squad_members = models.ManyToManyField(User,blank=True)
    def __str__(self) -> str:
        return self.name