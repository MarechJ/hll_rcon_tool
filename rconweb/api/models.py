from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db import models

from rconweb.settings import SECRET_KEY


class DjangoAPIKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    api_key = models.CharField(unique=True)
    date_created = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)
    notes = models.CharField(max_length=128, null=True, blank=True)

    default_permissions = ()

    def __str__(self) -> str:
        return f"{self.api_key}"

    def save(self, *args, **kwargs):
        """Hash the API key"""
        # If we don't include the salt, the hasher generates its own
        self.api_key = make_password(self.api_key, salt=SECRET_KEY.replace("$", ""))
        super().save()

    class Meta:
        ordering = ("date_modified",)
        verbose_name = "Django API Key"


class SteamPlayer(models.Model):
    """Associate a players in game ID (steam or windows) with their Django user"""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    steam_id_64 = models.CharField(
        max_length=100, verbose_name="Player ID", blank=True, default=""
    )
    default_permissions = ()


class RconUser(User):
    """api_rconuser table"""

    class Meta:
        default_permissions = ()
        permissions = (
            ("can_add_admin_roles", "Can add HLL game server admin roles to players"),
            ("can_add_map_to_rotation", "Can add a map to the rotation"),
            ("can_add_map_to_whitelist", "Can add a map to the votemap whitelist"),
            ("can_add_maps_to_rotation", "Can add maps to the rotation"),
            (
                "can_add_maps_to_whitelist",
                "Can add multiple maps to the votemap whitelist",
            ),
            ("can_add_player_comments", "Can add comments to a players profile"),
            ("can_add_player_watch", "Can add a watch to players"),
            ("can_add_vip", "Can add VIP status to players"),
            ("can_ban_profanities", "Can ban profanities (censored game chat)"),
            (
                "can_change_auto_broadcast_config",
                "Can change the automated broadcast settings",
            ),
            ("can_change_auto_settings", "Can change auto settings"),
            ("can_change_autobalance_enabled", "Can enable/disable autobalance"),
            (
                "can_change_autobalance_threshold",
                "Can change the autobalance threshold",
            ),
            ("can_change_broadcast_message", "Can change the broadcast message"),
            ("can_change_camera_config", "Can change camera notification settings"),
            ("can_change_current_map", "Can change the current map"),
            (
                "can_change_discord_webhooks",
                "Can change configured webhooks on the settings page",
            ),
            ("can_change_idle_autokick_time", "Can change the idle autokick time"),
            ("can_change_max_ping_autokick", "Can change the max ping autokick"),
            (
                "can_change_profanities",
                "Can add/remove profanities (censored game chat)",
            ),
            ("can_change_queue_length", "Can change the server queue size"),
            ("can_change_real_vip_config", "Can change the real VIP settings"),
            ("can_change_server_name", "Can change the server name"),
            (
                "can_change_shared_standard_messages",
                "Can change the shared standard messages",
            ),
            ("can_change_team_switch_cooldown", "Can change the team switch cooldown"),
            ("can_change_vip_slots", "Can change the number of reserved VIP slots"),
            ("can_change_votekick_autotoggle_config", "Can change votekick settings"),
            ("can_change_votekick_enabled", "Can enable/disable vote kicks"),
            ("can_change_votekick_threshold", "Can change vote kick thresholds"),
            ("can_change_votemap_config", "Can change the votemap settings"),
            ("can_change_welcome_message", "Can change the welcome (rules) message"),
            ("can_clear_crcon_cache", "Can clear the CRCON Redis cache"),
            ("can_download_vip_list", "Can download the VIP list"),
            ("can_flag_player", "Can add flags to players"),
            ("can_kick_players", "Can kick players"),
            ("can_message_players", "Can message players"),
            ("can_perma_ban_players", "Can permanently ban players"),
            ("can_punish_players", "Can punish players"),
            (
                "can_remove_admin_roles",
                "Can remove HLL game server admin roles from players",
            ),
            ("can_remove_all_vips", "Can remove all VIPs"),
            ("can_remove_map_from_rotation", "Can remove a map from the rotation"),
            (
                "can_remove_map_from_whitelist",
                "Can remove a map from the votemap whitelist",
            ),
            ("can_remove_maps_from_rotation", "Can remove maps from the rotation"),
            (
                "can_remove_maps_from_whitelist",
                "Can remove multiple maps from the votemap whitelist",
            ),
            ("can_remove_perma_bans", "Can remove permanent bans from players"),
            ("can_remove_player_watch", "Can remove a watch from players"),
            ("can_remove_temp_bans", "Can remove temporary bans from players"),
            ("can_remove_vip", "Can remove VIP status from players"),
            ("can_reset_map_whitelist", "Can reset the votemap whitelist"),
            ("can_reset_votekick_threshold", "Can reset votekick thresholds"),
            ("can_reset_votemap_state", "Can reset votemap selection & votes"),
            ("can_run_raw_commands", "Can send raw commands to the HLL game server"),
            ("can_set_map_whitelist", "Can set the votemap whitelist"),
            ("can_switch_players_immediately", "Can immediately switch players"),
            ("can_switch_players_on_death", "Can switch players on death"),
            ("can_temp_ban_players", "Can temporarily ban players"),
            ("can_toggle_services", "Can enable/disable services (automod, etc)"),
            ("can_unban_profanities", "Can unban profanities (censored game chat)"),
            ("can_unflag_player", "Can remove flags from players"),
            ("can_upload_vip_list", "Can upload a VIP list"),
            ("can_view_admin_groups", "Can view available admin roles"),
            (
                "can_view_admin_ids",
                "Can view the name/steam IDs/role of everyone with a HLL game server admin role",
            ),
            ("can_view_admins", "Can view users with HLL game server admin roles"),
            ("can_view_all_maps", "Can view all possible maps"),
            ("can_view_audit_logs", "Can view the can_view_audit_logs endpoint"),
            (
                "can_view_audit_logs_autocomplete",
                "Can view the get_audit_logs_autocomplete endpoint",
            ),
            (
                "can_view_auto_broadcast_config",
                "Can view the automated broadcast settings",
            ),
            ("can_view_auto_settings", "Can view auto settings"),
            ("can_view_autobalance_enabled", "Can view if autobalance is enabled"),
            ("can_view_autobalance_threshold", "Can view the autobalance threshold"),
            ("can_view_available_services", "Can view services (automod, etc)"),
            ("can_view_broadcast_message", "Can view the current broadcast message"),
            ("can_view_camera_config", "Can view camera notification settings"),
            ("can_view_connection_info", "Can view CRCON's connection info"),
            ("can_view_current_map", "Can view the currently playing map"),
            ("can_view_date_scoreboard", "Can view the date_scoreboard endpoint"),
            (
                "can_view_detailed_player_info",
                "Can view detailed player info (name, steam ID, loadout, squad, etc.)",
            ),
            (
                "can_view_discord_webhooks",
                "Can view configured webhooks on the settings page",
            ),
            (
                "can_view_game_logs",
                "Can view the get_logs endpoint (returns unparsed game logs)",
            ),
            ("can_view_gamestate", "Can view the current gamestate"),
            (
                "can_view_get_players",
                "Can view get_players endpoint (name, steam ID, VIP status and sessions) for all connected players",
            ),
            (
                "can_view_get_status",
                "Can view the get_status endpoint (server name, current map, player count)",
            ),
            ("can_view_historical_logs", "Can view historical logs"),
            ("can_view_idle_autokick_time", "Can view the idle autokick time"),
            ("can_view_ingame_admins", "Can view admins connected to the game server"),
            ("can_view_map_rotation", "Can view the current map rotation"),
            ("can_view_map_whitelist", "Can view the votemap whitelist"),
            ("can_view_max_ping_autokick", "Can view the max autokick ping"),
            ("can_view_next_map", "Can view the next map in the rotation"),
            ("can_view_online_admins", "Can view admins connected to CRCON"),
            (
                "can_view_online_console_admins",
                "Can view the player name of all connected players with a HLL game server admin role",
            ),
            (
                "can_view_other_crcon_servers",
                "Can view other servers hosted in the same CRCON (forward to all servers)",
            ),
            ("can_view_perma_bans", "Can view permanently banned players"),
            (
                "can_view_player_bans",
                "Can view all bans (temp/permanent) for a specific player",
            ),
            (
                "can_view_player_comments",
                "Can view comments added to a players profile",
            ),
            ("can_view_player_history", "Can view History > Players"),
            (
                "can_view_player_info",
                "Can view the get_player_info endpoint (Name, steam ID, country and steam bans)",
            ),
            ("can_view_player_messages", "Can view messages sent to players"),
            ("can_view_player_profile", "View the detailed player profile page"),
            ("can_view_player_slots", "Can view the current/max players on the server"),
            (
                "can_view_playerids",
                "Can view the get_playerids endpoint (name and steam IDs of connected players)",
            ),
            (
                "can_view_players",
                "Can view get_players endpoint for all connected players ",
            ),
            ("can_view_profanities", "Can view profanities (censored game chat)"),
            ("can_view_queue_length", "Can view the maximum size of the server queue"),
            ("can_view_real_vip_config", "Can view the real VIP settings"),
            ("can_view_recent_logs", "Can view recent logs (Live view)"),
            (
                "can_view_round_time_remaining",
                "Can view the amount of time left in the round",
            ),
            ("can_view_server_name", "Can view the server name"),
            (
                "can_view_shared_standard_messages",
                "Can view the shared standard messages",
            ),
            ("can_view_structured_logs", "Can view the get_structured_logs endpoint"),
            (
                "can_view_team_objective_scores",
                "Can view the number of objectives held by each team",
            ),
            (
                "can_view_team_switch_cooldown",
                "Can view the team switch cooldown value",
            ),
            ("can_view_detailed_players", "Can view get_detailed_players endpoint"),
            (
                "can_view_team_view",
                "Can view get_team_view endpoint (detailed player info by team for all connected players)",
            ),
            ("can_view_temp_bans", "Can view temporary banned players"),
            ("can_view_vip_count", "Can view the number of connected VIPs"),
            (
                "can_view_vip_ids",
                "Can view all players with VIP and their expiration timestamps",
            ),
            ("can_view_vip_slots", "Can view the number of reserved VIP slots"),
            ("can_view_votekick_autotoggle_config", "Can view votekick settings"),
            ("can_view_votekick_enabled", "Can view if vote kick is enabled"),
            ("can_view_votekick_threshold", "Can view the vote kick thresholds"),
            ("can_view_votemap_config", "Can view the votemap settings"),
            (
                "can_view_votemap_status",
                "Can view the current votemap status (votes, results, etc)",
            ),
            (
                "can_view_current_map_sequence",
                "Can view the current map shuffle sequence",
            ),
            ("can_view_map_shuffle_enabled", "Can view if map shuffle is enabled"),
            ("can_change_map_shuffle_enabled", "Can enable/disable map shuffle"),
            ("can_view_welcome_message", "Can view the server welcome message"),
            (
                "can_view_auto_mod_level_config",
                "Can view Auto Mod Level enforcement config",
            ),
            (
                "can_change_auto_mod_level_config",
                "Can change Auto Mod Level enforcement config",
            ),
            (
                "can_view_auto_mod_no_leader_config",
                "Can view Auto Mod No Leader enforcement config",
            ),
            (
                "can_change_auto_mod_no_leader_config",
                "Can change Auto Mod No Leader enforcement config",
            ),
            (
                "can_view_auto_mod_seeding_config",
                "Can view Auto Mod No Seeding enforcement config",
            ),
            (
                "can_change_auto_mod_seeding_config",
                "Can change Auto Mod No Seeding enforcement config",
            ),
            (
                "can_view_auto_mod_solo_tank_config",
                "Can view Auto Mod No Solo Tank enforcement config",
            ),
            (
                "can_change_auto_mod_solo_tank_config",
                "Can change Auto Mod No Solo Tank enforcement config",
            ),
            (
                "can_view_tk_ban_on_connect_config",
                "Can view team kill ban on connect config",
            ),
            (
                "can_change_tk_ban_on_connect_config",
                "Can change team kill ban on connect config",
            ),
            ("can_view_expired_vip_config", "Can view Expired VIP config"),
            ("can_change_expired_vip_config", "Can change Expired VIP config"),
            (
                "can_view_server_name_change_config",
                "Can view server name change (GSP credentials!) config",
            ),
            (
                "can_change_server_name_change_config",
                "Can change server name change (GSP credentials!) config",
            ),
            (
                "can_view_log_line_discord_webhook_config",
                "Can view log webhook (messages for log events) config",
            ),
            (
                "can_change_log_line_discord_webhook_config",
                "Can change log webhook (messages for log events) config",
            ),
            ("can_view_name_kick_config", "Can view kick players for names config"),
            ("can_change_name_kick_config", "Can change kick players for names config"),
            (
                "can_view_rcon_connection_settings_config",
                "Can view game server connection settings config",
            ),
            (
                "can_change_rcon_connection_settings_config",
                "Can change game server connection settings config",
            ),
            (
                "can_view_rcon_server_settings_config",
                "Can view general CRCON server settings",
            ),
            (
                "can_change_rcon_server_settings_config",
                "Can change general CRCON server settings",
            ),
            ("can_view_scorebot_config", "Can view scorebot config"),
            ("can_change_scorebot_config", "Can change scorebot config"),
            (
                "can_view_standard_broadcast_messages",
                "Can view shared broadcast messages",
            ),
            (
                "can_change_standard_broadcast_messages",
                "Can change shared broadcast messages",
            ),
            (
                "can_view_standard_punishment_messages",
                "Can view shared punishment messages",
            ),
            (
                "can_change_standard_punishment_messages",
                "Can change shared punishment messages",
            ),
            ("can_view_standard_welcome_messages", "Can view shared welcome messages"),
            (
                "can_change_standard_welcome_messages",
                "Can change shared welcome messages",
            ),
            ("can_view_steam_config", "Can view steam API config"),
            ("can_change_steam_config", "Can change steam API config"),
            (
                "can_view_vac_game_bans_config",
                "Can view VAC/Gameban ban on connect config",
            ),
            (
                "can_change_vac_game_bans_config",
                "Can change VAC/Gameban ban on connect config",
            ),
            (
                "can_view_admin_pings_discord_webhooks_config",
                "Can view Discord admin ping config",
            ),
            (
                "can_change_admin_pings_discord_webhooks_config",
                "Can change Discord admin ping config",
            ),
            ("can_view_audit_discord_webhooks_config", "Can view Discord audit config"),
            (
                "can_change_audit_discord_webhooks_config",
                "Can change Discord audit config",
            ),
            (
                "can_view_camera_discord_webhooks_config",
                "Can view Discord admin cam notification config",
            ),
            (
                "can_change_camera_discord_webhooks_config",
                "Can change Discord admin cam notification config",
            ),
            (
                "can_view_chat_discord_webhooks_config",
                "Can view Discord chat notification config",
            ),
            (
                "can_change_chat_discord_webhooks_config",
                "Can change Discord chat notification config",
            ),
            (
                "can_view_kills_discord_webhooks_config",
                "Can view Discord team/teamkill notification config",
            ),
            (
                "can_change_kills_discord_webhooks_config",
                "Can change Discord team/teamkill notification config",
            ),
            (
                "can_view_watchlist_discord_webhooks_config",
                "Can view Discord player watchlist notification config",
            ),
            (
                "can_change_watchlist_discord_webhooks_config",
                "Can change Discord player watchlist notification config",
            ),
            (
                "can_restart_webserver",
                "Can restart the webserver (Not a complete Docker restart)",
            ),
            ("can_view_chat_commands_config", "Can view the chat commands config"),
            ("can_change_chat_commands_config", "Can change the chat commands config"),
            (
                "can_view_rcon_chat_commands_config",
                "Can view the rcon chat commands config",
            ),
            (
                "can_change_rcon_chat_commands_config",
                "Can change rcon the chat commands config",
            ),
            ("can_view_log_stream_config", "Can view the Log Stream config"),
            ("can_change_log_stream_config", "Can change the Log Stream config"),
            ("can_view_blacklists", "Can view available blacklists"),
            ("can_add_blacklist_records", "Can add players to blacklists"),
            (
                "can_change_blacklist_records",
                "Can unblacklist players and edit blacklist records",
            ),
            ("can_delete_blacklist_records", "Can delete blacklist records"),
            ("can_create_blacklists", "Can create blacklists"),
            ("can_change_blacklists", "Can change blacklists"),
            ("can_delete_blacklists", "Can delete blacklists"),
            ("can_change_game_layout", "Can change game layout"),
            ("can_view_message_templates", "Can view shared message templates"),
            ("can_add_message_templates", "Can add new shared message templates"),
            ("can_delete_message_templates", "Can delete shared message templates"),
            ("can_edit_message_templates", "Can edit shared message templates"),
            ("can_view_seed_vip_config", "Can view the Seed VIP config"),
            ("can_change_seed_vip_config", "Can change the Seed VIP config"),
            (
                "can_view_webhook_queues",
                "Can view information about the webhook service",
            ),
            (
                "can_change_webhook_queues",
                "Can remove messages from the webhook queue service",
            ),
        )
