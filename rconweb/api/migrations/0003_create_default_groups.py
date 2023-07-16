# Generated by Django 3.2.18 on 2023-04-10 06:10

from django.contrib.auth.management import create_permissions
from django.db import migrations

GROUPS = [
    (
        # Default owner group, all permissions
        "owner",
        (
            "can_add_admin_roles",
            "can_add_map_to_rotation",
            "can_add_map_to_whitelist",
            "can_add_maps_to_rotation",
            "can_add_maps_to_whitelist",
            "can_add_player_comments",
            "can_add_player_watch",
            "can_add_vip",
            "can_ban_profanities",
            "can_blacklist_players",
            "can_change_auto_broadcast_config",
            "can_change_auto_settings",
            "can_change_autobalance_enabled",
            "can_change_autobalance_threshold",
            "can_change_broadcast_message",
            "can_change_camera_config",
            "can_change_current_map",
            "can_change_discord_webhooks",
            "can_change_idle_autokick_time",
            "can_change_map_shuffle_enabled",
            "can_change_max_ping_autokick",
            "can_change_profanities",
            "can_change_queue_length",
            "can_change_real_vip_config",
            "can_change_server_name",
            "can_change_shared_standard_messages",
            "can_change_team_switch_cooldown",
            "can_change_vip_slots",
            "can_change_votekick_autotoggle_config",
            "can_change_votekick_enabled",
            "can_change_votekick_threshold",
            "can_change_votemap_config",
            "can_change_welcome_message",
            "can_clear_crcon_cache",
            "can_download_vip_list",
            "can_flag_player",
            "can_kick_players",
            "can_message_players",
            "can_perma_ban_players",
            "can_punish_players",
            "can_remove_admin_roles",
            "can_remove_all_vips",
            "can_remove_map_from_rotation",
            "can_remove_map_from_whitelist",
            "can_remove_maps_from_rotation",
            "can_remove_maps_from_whitelist",
            "can_remove_perma_bans",
            "can_remove_player_watch",
            "can_remove_temp_bans",
            "can_remove_vip",
            "can_reset_map_whitelist",
            "can_reset_votekick_threshold",
            "can_reset_votemap_state",
            "can_run_raw_commands",
            "can_set_map_whitelist",
            "can_switch_players_immediately",
            "can_switch_players_on_death",
            "can_temp_ban_players",
            "can_toggle_services",
            "can_unban_profanities",
            "can_unblacklist_players",
            "can_unflag_player",
            "can_upload_vip_list",
            "can_view_admin_groups",
            "can_view_admin_ids",
            "can_view_admins",
            "can_view_all_maps",
            "can_view_audit_logs_autocomplete",
            "can_view_audit_logs",
            "can_view_auto_broadcast_config",
            "can_view_auto_settings",
            "can_view_autobalance_enabled",
            "can_view_autobalance_threshold",
            "can_view_available_services",
            "can_view_broadcast_message",
            "can_view_camera_config",
            "can_view_connection_info",
            "can_view_current_map_sequence",
            "can_view_current_map",
            "can_view_date_scoreboard",
            "can_view_detailed_player_info",
            "can_view_discord_webhooks",
            "can_view_game_logs",
            "can_view_gamestate",
            "can_view_get_players",
            "can_view_get_status",
            "can_view_historical_logs",
            "can_view_idle_autokick_time",
            "can_view_ingame_admins",
            "can_view_map_rotation",
            "can_view_map_shuffle_enabled",
            "can_view_map_whitelist",
            "can_view_max_ping_autokick",
            "can_view_next_map",
            "can_view_online_admins",
            "can_view_online_console_admins",
            "can_view_other_crcon_servers",
            "can_view_perma_bans",
            "can_view_player_bans",
            "can_view_player_comments",
            "can_view_player_history",
            "can_view_player_info",
            "can_view_player_messages",
            "can_view_player_profile",
            "can_view_player_slots",
            "can_view_playerids",
            "can_view_players",
            "can_view_profanities",
            "can_view_queue_length",
            "can_view_real_vip_config",
            "can_view_recent_logs",
            "can_view_round_time_remaining",
            "can_view_scoreboard",
            "can_view_server_name",
            "can_view_server_stats",
            "can_view_shared_standard_messages",
            "can_view_structured_logs",
            "can_view_team_objective_scores",
            "can_view_team_switch_cooldown",
            "can_view_detailed_players",
            "can_view_team_view",
            "can_view_teamkills_boards",
            "can_view_temp_bans",
            "can_view_timed_logs",
            "can_view_vip_count",
            "can_view_vip_ids",
            "can_view_vip_slots",
            "can_view_votekick_autotoggle_config",
            "can_view_votekick_enabled",
            "can_view_votekick_threshold",
            "can_view_votemap_config",
            "can_view_votemap_status",
            "can_view_welcome_message",
        ),
    ),
    (
        # Default admin group, full access to everything except can_run_raw_commands
        "admin",
        (
            "can_add_admin_roles",
            "can_add_map_to_rotation",
            "can_add_map_to_whitelist",
            "can_add_maps_to_rotation",
            "can_add_maps_to_whitelist",
            "can_add_player_comments",
            "can_add_player_watch",
            "can_add_vip",
            "can_ban_profanities",
            "can_blacklist_players",
            "can_change_auto_broadcast_config",
            "can_change_auto_settings",
            "can_change_autobalance_enabled",
            "can_change_autobalance_threshold",
            "can_change_broadcast_message",
            "can_change_camera_config",
            "can_change_current_map",
            "can_change_discord_webhooks",
            "can_change_idle_autokick_time",
            "can_change_map_shuffle_enabled",
            "can_change_max_ping_autokick",
            "can_change_profanities",
            "can_change_queue_length",
            "can_change_real_vip_config",
            "can_change_server_name",
            "can_change_shared_standard_messages",
            "can_change_team_switch_cooldown",
            "can_change_vip_slots",
            "can_change_votekick_autotoggle_config",
            "can_change_votekick_enabled",
            "can_change_votekick_threshold",
            "can_change_votemap_config",
            "can_change_welcome_message",
            "can_clear_crcon_cache",
            "can_download_vip_list",
            "can_flag_player",
            "can_kick_players",
            "can_message_players",
            "can_perma_ban_players",
            "can_punish_players",
            "can_remove_admin_roles",
            "can_remove_all_vips",
            "can_remove_map_from_rotation",
            "can_remove_map_from_whitelist",
            "can_remove_maps_from_rotation",
            "can_remove_maps_from_whitelist",
            "can_remove_perma_bans",
            "can_remove_player_watch",
            "can_remove_temp_bans",
            "can_remove_vip",
            "can_reset_map_whitelist",
            "can_reset_votekick_threshold",
            "can_reset_votemap_state",
            "can_set_map_whitelist",
            "can_switch_players_immediately",
            "can_switch_players_on_death",
            "can_temp_ban_players",
            "can_toggle_services",
            "can_unban_profanities",
            "can_unblacklist_players",
            "can_unflag_player",
            "can_upload_vip_list",
            "can_view_admin_groups",
            "can_view_admin_ids",
            "can_view_admins",
            "can_view_all_maps",
            "can_view_audit_logs_autocomplete",
            "can_view_audit_logs",
            "can_view_auto_broadcast_config",
            "can_view_auto_settings",
            "can_view_autobalance_enabled",
            "can_view_autobalance_threshold",
            "can_view_available_services",
            "can_view_broadcast_message",
            "can_view_camera_config",
            "can_view_connection_info",
            "can_view_current_map_sequence",
            "can_view_current_map",
            "can_view_date_scoreboard",
            "can_view_detailed_player_info",
            "can_view_discord_webhooks",
            "can_view_game_logs",
            "can_view_gamestate",
            "can_view_get_players",
            "can_view_get_status",
            "can_view_historical_logs",
            "can_view_idle_autokick_time",
            "can_view_ingame_admins",
            "can_view_map_rotation",
            "can_view_map_shuffle_enabled",
            "can_view_map_whitelist",
            "can_view_max_ping_autokick",
            "can_view_next_map",
            "can_view_online_admins",
            "can_view_online_console_admins",
            "can_view_other_crcon_servers",
            "can_view_perma_bans",
            "can_view_player_bans",
            "can_view_player_comments",
            "can_view_player_history",
            "can_view_player_info",
            "can_view_player_messages",
            "can_view_player_profile",
            "can_view_player_slots",
            "can_view_playerids",
            "can_view_players",
            "can_view_profanities",
            "can_view_queue_length",
            "can_view_real_vip_config",
            "can_view_recent_logs",
            "can_view_round_time_remaining",
            "can_view_scoreboard",
            "can_view_server_name",
            "can_view_server_stats",
            "can_view_shared_standard_messages",
            "can_view_structured_logs",
            "can_view_team_objective_scores",
            "can_view_team_switch_cooldown",
            "can_view_detailed_players",
            "can_view_team_view",
            "can_view_teamkills_boards",
            "can_view_temp_bans",
            "can_view_timed_logs",
            "can_view_vip_count",
            "can_view_vip_ids",
            "can_view_vip_slots",
            "can_view_votekick_autotoggle_config",
            "can_view_votekick_enabled",
            "can_view_votekick_threshold",
            "can_view_votemap_config",
            "can_view_votemap_status",
            "can_view_welcome_message",
        ),
    ),
    (
        # Default moderator group, reduced permissions but full read access
        "moderator",
        (
            "can_add_player_comments",
            "can_add_player_watch",
            "can_blacklist_players",
            "can_flag_player",
            "can_kick_players",
            "can_message_players",
            "can_perma_ban_players",
            "can_punish_players",
            "can_remove_perma_bans",
            "can_remove_player_watch",
            "can_remove_temp_bans",
            "can_switch_players_immediately",
            "can_switch_players_on_death",
            "can_temp_ban_players",
            "can_unblacklist_players",
            "can_unflag_player",
            "can_view_admin_groups",
            "can_view_admin_ids",
            "can_view_admins",
            "can_view_all_maps",
            "can_view_audit_logs_autocomplete",
            "can_view_audit_logs",
            "can_view_auto_broadcast_config",
            "can_view_auto_settings",
            "can_view_autobalance_enabled",
            "can_view_autobalance_threshold",
            "can_view_available_services",
            "can_view_broadcast_message",
            "can_view_camera_config",
            "can_view_connection_info",
            "can_view_current_map_sequence",
            "can_view_current_map",
            "can_view_date_scoreboard",
            "can_view_detailed_player_info",
            "can_view_discord_webhooks",
            "can_view_game_logs",
            "can_view_gamestate",
            "can_view_get_players",
            "can_view_get_status",
            "can_view_historical_logs",
            "can_view_idle_autokick_time",
            "can_view_ingame_admins",
            "can_view_map_rotation",
            "can_view_map_shuffle_enabled",
            "can_view_map_whitelist",
            "can_view_max_ping_autokick",
            "can_view_next_map",
            "can_view_online_admins",
            "can_view_online_console_admins",
            "can_view_other_crcon_servers",
            "can_view_perma_bans",
            "can_view_player_bans",
            "can_view_player_comments",
            "can_view_player_history",
            "can_view_player_info",
            "can_view_player_messages",
            "can_view_player_profile",
            "can_view_player_slots",
            "can_view_playerids",
            "can_view_players",
            "can_view_profanities",
            "can_view_queue_length",
            "can_view_real_vip_config",
            "can_view_recent_logs",
            "can_view_round_time_remaining",
            "can_view_scoreboard",
            "can_view_server_name",
            "can_view_server_stats",
            "can_view_shared_standard_messages",
            "can_view_structured_logs",
            "can_view_team_objective_scores",
            "can_view_team_switch_cooldown",
            "can_view_detailed_players",
            "can_view_team_view",
            "can_view_teamkills_boards",
            "can_view_temp_bans",
            "can_view_timed_logs",
            "can_view_vip_count",
            "can_view_vip_ids",
            "can_view_vip_slots",
            "can_view_votekick_autotoggle_config",
            "can_view_votekick_enabled",
            "can_view_votekick_threshold",
            "can_view_votemap_config",
            "can_view_votemap_status",
            "can_view_welcome_message",
        ),
    ),
    (
        # Default read_only group, read access only
        "read_only",
        (
            "can_view_admin_groups",
            "can_view_admin_ids",
            "can_view_admins",
            "can_view_all_maps",
            "can_view_audit_logs_autocomplete",
            "can_view_audit_logs",
            "can_view_auto_broadcast_config",
            "can_view_auto_settings",
            "can_view_autobalance_enabled",
            "can_view_autobalance_threshold",
            "can_view_available_services",
            "can_view_broadcast_message",
            "can_view_camera_config",
            "can_view_connection_info",
            "can_view_current_map_sequence",
            "can_view_current_map",
            "can_view_date_scoreboard",
            "can_view_detailed_player_info",
            "can_view_discord_webhooks",
            "can_view_game_logs",
            "can_view_gamestate",
            "can_view_get_players",
            "can_view_get_status",
            "can_view_historical_logs",
            "can_view_idle_autokick_time",
            "can_view_ingame_admins",
            "can_view_map_rotation",
            "can_view_map_shuffle_enabled",
            "can_view_map_whitelist",
            "can_view_max_ping_autokick",
            "can_view_next_map",
            "can_view_online_admins",
            "can_view_online_console_admins",
            "can_view_other_crcon_servers",
            "can_view_perma_bans",
            "can_view_player_bans",
            "can_view_player_comments",
            "can_view_player_history",
            "can_view_player_info",
            "can_view_player_messages",
            "can_view_player_profile",
            "can_view_player_slots",
            "can_view_playerids",
            "can_view_players",
            "can_view_profanities",
            "can_view_queue_length",
            "can_view_real_vip_config",
            "can_view_recent_logs",
            "can_view_round_time_remaining",
            "can_view_scoreboard",
            "can_view_server_name",
            "can_view_server_stats",
            "can_view_shared_standard_messages",
            "can_view_structured_logs",
            "can_view_team_objective_scores",
            "can_view_team_switch_cooldown",
            "can_view_detailed_players",
            "can_view_team_view",
            "can_view_teamkills_boards",
            "can_view_temp_bans",
            "can_view_timed_logs",
            "can_view_vip_count",
            "can_view_vip_ids",
            "can_view_vip_slots",
            "can_view_votekick_autotoggle_config",
            "can_view_votekick_enabled",
            "can_view_votekick_threshold",
            "can_view_votemap_config",
            "can_view_votemap_status",
            "can_view_welcome_message",
        ),
    ),
]


def create_default_groups(apps, schema_editor):
    Group = apps.get_model("auth.Group")
    Permission = apps.get_model("auth.Permission")
    ContentType = apps.get_model("contenttypes.ContentType")
    RconUser = apps.get_model(f"api.RconUser")

    # Have to manually ensure that permissions are created from the
    # prior migration or this migration will fail
    app_config = apps.get_app_config("api")
    app_config.models_module = True
    create_permissions(app_config=app_config)
    app_config.models_module = None

    content_type = ContentType.objects.get_for_model(RconUser)
    for group_name, permissions in GROUPS:
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            group = Group.objects.create(name=group_name)

        for raw_permission in permissions:
            # Permissions are created in an earlier migration so they should exist
            # If they don't we want to fail now and fix it
            permission = Permission.objects.get(
                content_type=content_type, codename=raw_permission
            )
            group.permissions.add(permission)


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0002_rconuser"),
    ]

    operations = [migrations.RunPython(create_default_groups)]
