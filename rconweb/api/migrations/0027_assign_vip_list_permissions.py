# ruff: noqa: RUF012

from django.db import migrations

PERMISSIONS = {
    "can_view_vip_lists": "Can view VIP lists and records",
    "can_create_vip_lists": "Can create VIP lists",
    "can_change_vip_lists": "Can change VIP lists",
    "can_delete_vip_lists": "Can delete VIP lists",
    "can_add_vip_list_records": "Can add players to VIP lists",
    "can_change_vip_list_records": "Can change VIP list records",
    "can_delete_vip_list_records": "Can delete VIP list records",
}

DEFAULT_PRIVILEGED_GROUPS = (
    "owner",
    "admin",
)


def assign_vip_list_permissions(apps, schema_editor):
    database = schema_editor.connection.alias
    ContentType = apps.get_model("contenttypes", "ContentType")
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    content_type, _ = ContentType.objects.using(database).get_or_create(
        app_label="api",
        model="rconuser",
    )

    permissions = []
    for codename, name in PERMISSIONS.items():
        permission, _ = Permission.objects.using(database).get_or_create(
            content_type_id=content_type.pk,
            codename=codename,
            defaults={"name": name},
        )

        if permission.name != name:
            permission.name = name
            permission.save(
                using=database,
                update_fields=["name"],
            )

        permissions.append(permission)

    groups = Group.objects.using(database).filter(name__in=DEFAULT_PRIVILEGED_GROUPS)
    for group in groups:
        group.permissions.add(*permissions)


def remove_vip_list_permissions(apps, schema_editor):
    database = schema_editor.connection.alias
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    permissions = Permission.objects.using(database).filter(
        content_type__app_label="api",
        content_type__model="rconuser",
        codename__in=PERMISSIONS,
    )

    groups = Group.objects.using(database).filter(name__in=DEFAULT_PRIVILEGED_GROUPS)
    for group in groups:
        group.permissions.remove(*permissions)

    permissions.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0026_add_vip_list_permissions"),
    ]

    operations = [
        migrations.RunPython(
            assign_vip_list_permissions,
            remove_vip_list_permissions,
        ),
    ]
