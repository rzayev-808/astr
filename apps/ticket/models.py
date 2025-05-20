from django.db import models
from user.models import User
from squads.models import Squad
from task.models import Task


class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    squad = models.ForeignKey(Squad, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE,blank=True,null=True)
    date = models.DateTimeField(auto_now_add=True)
    title = models.TextField()
    
    
    def __str__(self):
        return self.title
    

class Answer(models.Model):
    ticket = models.ForeignKey(Ticket,on_delete=models.CASCADE)
    answer = models.TextField()
    
    def __str__(self):
        return self.answer
    
    
    