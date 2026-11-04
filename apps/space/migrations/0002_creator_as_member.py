# Mövcud space-lərdə yaradan members siyahısında yox idi; bir dəfəlik əlavə olunur.

from django.db import migrations


def add_creators(apps, schema_editor):
    Space = apps.get_model("space", "Space")
    for space in Space.objects.all().iterator():
        if space.creater_user_id:
            space.members.add(space.creater_user_id)


class Migration(migrations.Migration):

    dependencies = [
        ("space", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(add_creators, migrations.RunPython.noop),
    ]
