# Dəvətə gizli kod (token) əlavə olunur. Köhnə dəvətlərə də hər birinə ayrıca kod verilir,
# ona görə üç addımdır: əvvəl boş sahə, sonra doldurma, sonra "unikal" şərti.

from django.db import migrations, models

import invite.models


def fill_tokens(apps, schema_editor):
    Invite = apps.get_model("invite", "Invite")
    for inv in Invite.objects.filter(token__isnull=True):
        inv.token = invite.models.generate_invite_token()
        inv.save(update_fields=["token"])


class Migration(migrations.Migration):

    dependencies = [
        ("invite", "0002_invite_invited_by_invite_space"),
    ]

    operations = [
        migrations.AddField(
            model_name="invite",
            name="token",
            field=models.CharField(max_length=64, null=True, editable=False),
        ),
        migrations.RunPython(fill_tokens, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="invite",
            name="token",
            field=models.CharField(
                default=invite.models.generate_invite_token,
                editable=False,
                max_length=64,
                unique=True,
            ),
        ),
    ]
