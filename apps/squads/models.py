from django.db import models
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from space.models import Space
from user.models import User

class Squad(models.Model):
    name = models.CharField(max_length=200)
    create_date = models.DateTimeField(auto_now_add=True)
    space = models.ForeignKey(Space,on_delete=models.CASCADE,related_name="squad_space")
    squad_members = models.ManyToManyField(User,blank=True)
    def __str__(self) -> str:
        return self.name


def _space_member_ids(space):
    ids = set(space.members.values_list("id", flat=True))
    if space.creater_user_id:
        ids.add(space.creater_user_id)
    return ids


@receiver(post_save, sender=Squad)
def fill_squad_with_space_members(sender, instance, created, *args, **kwargs):
    """Yeni squad: default olaraq space-in bütün üzvləri (yaradan daxil) squad-ın üzvü olur.

    Front-end task yaradanda üzv seçimini squad üzvlərindən götürür; boş squad-da heç kim seçilmir.
    Squad üzvlərini sonradan azaltmaq olar (PATCH squad_members). Yaradılarkən squad_members açıq
    göndərilibsə, serializer onu bu siyahının üstünə yazır — açıq seçim qalır.
    """
    if created:
        instance.squad_members.add(*_space_member_ids(instance.space))


@receiver(m2m_changed, sender=Space.members.through)
def sync_space_members_to_squads(sender, instance, action, pk_set, reverse, *args, **kwargs):
    """Space-ə üzv əlavə olunanda (dəvət qəbulu, əl ilə əlavə) space-in bütün squad-larına da düşür;
    space-dən çıxarılanda squad-lardan da çıxır ki, girişi qalmasın."""
    if reverse or not pk_set:
        return
    if action == "post_add":
        for squad in instance.squad_space.all():
            squad.squad_members.add(*pk_set)
    elif action == "post_remove":
        for squad in instance.squad_space.all():
            squad.squad_members.remove(*pk_set)
