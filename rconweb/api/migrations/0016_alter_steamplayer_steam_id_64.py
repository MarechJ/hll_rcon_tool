# Generated by Django 4.2.15 on 2024-09-23 20:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0015_alter_rconuser_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="steamplayer",
            name="steam_id_64",
            field=models.CharField(
                blank=True, default="", max_length=100, verbose_name="Player ID"
            ),
        ),
    ]
