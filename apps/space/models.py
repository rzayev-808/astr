from django.db import models
from user.models import User
from pricing.models import Pricing
from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver

def create_default_name():
    import random
    name = "spc-" + str(random.randint(1000,1000000))
    return name


class Space(models.Model):
    creater_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="crt_usr")
    space_name = models.CharField(max_length=200,blank=True,null=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    company = models.CharField(max_length=200,blank=True,null=True)
    company_descrption = models.TextField(blank=True,null=True)
    pricing_plans = models.ForeignKey(Pricing,on_delete=models.CASCADE)
    members = models.ManyToManyField(User,blank=True,related_name="member")
    space_logo = models.FileField(upload_to="space_logo",blank=True,null=True)

    def __str__(self) -> str:
        return self.creater_user.fullname

@receiver(post_save, sender=User)
def create_default_space(sender, instance, created, *args, **kwargs):
    if created:
        Space.objects.get_or_create(
            space_name = create_default_name(),

            creater_user_id=instance.id,
            pricing_plans_id = Pricing.objects.filter(name="Free").last().id
        )


@receiver(post_save, sender=Space)
def add_creator_as_member(sender, instance, created, *args, **kwargs):
    """Space-i yaradan həmişə members siyahısında da olsun (front-end üzv seçimini bu siyahıdan edir)."""
    if created and instance.creater_user_id:
        instance.members.add(instance.creater_user_id)
