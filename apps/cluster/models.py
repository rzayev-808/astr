from django.db import models
from user.models import User
from space.models import Space

class Cluster(models.Model):
    name = models.CharField(max_length=200)
    create_date = models.DateTimeField(auto_now_add=True)
    space = models.ForeignKey(Space,on_delete=models.CASCADE,related_name="cluster_space")

    def __str__(self) -> str:
        return self.name