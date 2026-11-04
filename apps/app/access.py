"""Kimin nəyə girişi var — qayda bir yerdə, bütün view-lar bunu işlədir.

    space   → yaradan və ya üzv
    cluster → space-ə girişi olan (space səviyyəsindədir)
    squad   → space-ə girişi olan (yaradan və ya üzv) və ya squad-ın üzvü
              (başqa space-lərin squad-ları görünmür; dəvətlə gələn adam öz space-inin
               bütün squad-larında işləyə bilir)
    task    → squad-a girişi olan və ya task üzvü

`*_q(user, prefix)` Q-filtr qaytarır; prefix ilə əlaqəli modeldən də istifadə olunur,
məs. task üçün squad_q(user, "squad__"). `accessible_*` hazır queryset verir
(login olmayan üçün boş), `can_access_*` isə bəli/xeyr.
"""
from django.db.models import Q


def _logged_in(user):
    return user is not None and getattr(user, "is_authenticated", False)


def space_q(user, prefix=""):
    return Q(**{f"{prefix}creater_user": user}) | Q(**{f"{prefix}members": user})


def squad_q(user, prefix=""):
    return space_q(user, f"{prefix}space__") | Q(**{f"{prefix}squad_members": user})


def task_q(user, prefix=""):
    return squad_q(user, f"{prefix}squad__") | Q(**{f"{prefix}members": user})


def accessible_spaces(user):
    from space.models import Space
    if not _logged_in(user):
        return Space.objects.none()
    return Space.objects.filter(space_q(user)).distinct()


def accessible_clusters(user):
    from cluster.models import Cluster
    if not _logged_in(user):
        return Cluster.objects.none()
    return Cluster.objects.filter(space_q(user, "space__")).distinct()


def accessible_squads(user):
    from squads.models import Squad
    if not _logged_in(user):
        return Squad.objects.none()
    return Squad.objects.filter(squad_q(user)).distinct()


def accessible_tasks(user):
    from task.models import Task
    if not _logged_in(user):
        return Task.objects.none()
    return Task.objects.filter(task_q(user)).distinct()


def can_access_space(user, space):
    return accessible_spaces(user).filter(pk=space.pk).exists()


def can_access_squad(user, squad):
    return accessible_squads(user).filter(pk=squad.pk).exists()


def can_access_task(user, task):
    return accessible_tasks(user).filter(pk=task.pk).exists()
