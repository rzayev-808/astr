from django.db import models
from user.models import User
from squads.models import Squad

STATIS_CHOICES = [
    ("Backlog", "Backlog"),
    ("Progress", "Progress"),
    ("To Do", "To Do"),
    ("Review", "Review"),
    ("Done", "Done"),
]



class Project(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class DoD(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Topics(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class SubTasks(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Task(models.Model):
    squad = models.ForeignKey(Squad,on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField()
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    description = models.TextField()
    task_is_dependent_on = models.ForeignKey("Task",on_delete=models.CASCADE,blank=True,null=True,related_name="task_is_dependent")
    dependent_task = models.ForeignKey("Task",on_delete=models.CASCADE,blank=True,null=True,related_name="dependents")
    dod = models.ManyToManyField(DoD,blank=True,)
    topics = models.ManyToManyField(Topics,blank=True)
    subtasks = models.ManyToManyField(SubTasks,blank=True)
    story_point = models.CharField(max_length=200)
    members = models.ManyToManyField(User,blank=True,related_name="task_member")
    status = models.CharField(max_length=100,choices=STATIS_CHOICES,default=[0][0])


    def __str__(self):
        return "{}-{}".format(self.squad.name,self.status)




class FileTaks(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE,related_name="files")
    file = models.FileField()

    def __str__(self):
        return str(self.task)


class Comment(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE,related_name="comments")
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.task)
