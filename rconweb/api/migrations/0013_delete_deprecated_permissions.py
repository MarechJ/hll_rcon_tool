from __future__ import unicode_literals
from django.db import migrations

DEPRECATED_PERMISSIONS = (
    "can_blacklist_players",
    "can_unblacklist_players",
    "can_view_scoreboard",
    "can_view_server_stats",
    "can_view_teamkills_boards",
    "can_view_timed_logs",
)

from logging import getLogger

logger = getLogger(__name__)


def add_permissions(apps, schema_editor):
    pass


def remove_permissions(apps, schema_editor):
    """Reverse the above additions of permissions."""
    Permission = apps.get_model("auth.Permission")
    ContentType = apps.get_model("contenttypes.ContentType")
    RconUser = apps.get_model(f"api.RconUser")

    content_type = ContentType.objects.get_for_model(RconUser)

    # This cascades to Group
    permissions = Permission.objects.filter(
        content_type=content_type,
        codename__in=DEPRECATED_PERMISSIONS,
    )
    for p in permissions:
        try:
            p.delete()
        # permissions.delete()
        except RconUser.DoesNotExist:
            logger.info(f"Can't delete permission={p}")


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0012_alter_rconuser_options_alter_steamplayer_steam_id_64"),
    ]
    operations = [
        migrations.RunPython(remove_permissions, add_permissions),
    ]
