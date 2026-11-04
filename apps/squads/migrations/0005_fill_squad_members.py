# Mövcud squad-lara space-in üzvləri (yaradan daxil) bir dəfəlik əlavə olunur.
# Bundan sonra bu, siqnallarla avtomatik gedir (bax: squads/models.py).

from django.db import migrations


def fill_members(apps, schema_editor):
    Squad = apps.get_model("squads", "Squad")
    for squad in Squad.objects.select_related("space").iterator():
        space = squad.space
        ids = set(space.members.values_list("id", flat=True))
        if space.creater_user_id:
            ids.add(space.creater_user_id)
        if ids:
            squad.squad_members.add(*ids)


class Migration(migrations.Migration):

    dependencies = [
        ("squads", "0004_rename_members_squad_squad_members"),
        ("space", "0002_creator_as_member"),
    ]

    operations = [
        migrations.RunPython(fill_members, migrations.RunPython.noop),
    ]
