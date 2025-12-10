# Generated manually on 2025-11-04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("api", "0022_alter_rconuser_options"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserServerPermission",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "server_number",
                    models.IntegerField(help_text="Server number that the user can view"),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="server_permissions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "User Server Permission",
                "verbose_name_plural": "User Server Permissions",
                "ordering": ("server_number",),
                "default_permissions": (),
            },
        ),
        migrations.AlterUniqueTogether(
            name="userserverpermission",
            unique_together={("user", "server_number")},
        ),
    ]

