export const permissions = [
  {
    permission: 'can_change_vip_slots',
    description: 'Can change the number of reserved VIP slots'
  },
  {
    permission: 'can_restart_webserver',
    description: 'Can restart the webserver (Not a complete Docker restart)'
  },
  {
    permission: 'can_view_structured_logs',
    description: 'Can view the get_structured_logs endpoint'
  },
  {
    permission: 'can_view_rcon_server_settings_config',
    description: 'Can view general CRCON server settings'
  },
  {
    permission: 'can_view_votekick_threshold',
    description: 'Can view the vote kick thresholds'
  },
  {
    permission: 'can_add_map_to_whitelist',
    description: 'Can add a map to the votemap whitelist'
  },
  {
    permission: 'can_view_player_messages',
    description: 'Can view messages sent to players'
  },
  {
    permission: 'can_change_expired_vip_config',
    description: 'Can change Expired VIP config'
  },
  {
    permission: 'can_change_server_name',
    description: 'Can change the server name'
  },
  {
    permission: 'can_change_tk_ban_on_connect_config',
    description: 'Can change team kill ban on connect config'
  },
  {
    permission: 'can_change_standard_welcome_messages',
    description: 'Can change shared welcome messages'
  },
  {
    permission: 'can_change_current_map',
    description: 'Can change the current map'
  },
  {
    permission: 'can_view_vip_count',
    description: 'Can view the number of connected VIPs'
  },
  {
    permission: 'can_change_auto_mod_level_config',
    description: 'Can change Auto Mod Level enforcement config'
  },
  {
    permission: 'can_view_team_switch_cooldown',
    description: 'Can view the team switch cooldown value'
  },
  {
    permission: 'can_change_log_stream_config',
    description: 'Can change the Log Stream config'
  },
  {
    permission: 'can_change_auto_mod_no_leader_config',
    description: 'Can change Auto Mod No Leader enforcement config'
  },
  {
    permission: 'can_change_blacklist_records',
    description: 'Can unblacklist players and edit blacklist records'
  },
  {
    permission: 'can_remove_admin_roles',
    description: 'Can remove HLL game server admin roles from players'
  },
  {
    permission: 'can_view_admins',
    description: 'Can view users with HLL game server admin roles'
  },
  {
    permission: 'can_view_standard_welcome_messages',
    description: 'Can view shared welcome messages'
  },
  {
    permission: 'can_temp_ban_players',
    description: 'Can temporarily ban players'
  },
  {
    permission: 'can_view_votemap_config',
    description: 'Can view the votemap settings'
  },
  { permission: 'add_logentry', description: 'Can add log entry' },
  {
    permission: 'can_remove_map_from_rotation',
    description: 'Can remove a map from the rotation'
  },
  {
    permission: 'can_remove_map_from_whitelist',
    description: 'Can remove a map from the votemap whitelist'
  },
  {
    permission: 'can_view_vip_ids',
    description: 'Can view all players with VIP and their expiration timestamps'
  },
  {
    permission: 'change_contenttype',
    description: 'Can change content type'
  },
  {
    permission: 'can_view_expired_vip_config',
    description: 'Can view Expired VIP config'
  },
  {
    permission: 'can_view_auto_settings',
    description: 'Can view auto settings'
  },
  {
    permission: 'can_view_autobalance_enabled',
    description: 'Can view if autobalance is enabled'
  },
  {
    permission: 'can_view_votekick_enabled',
    description: 'Can view if vote kick is enabled'
  },
  {
    permission: 'can_unflag_player',
    description: 'Can remove flags from players'
  },
  {
    permission: 'can_view_player_slots',
    description: 'Can view the current/max players on the server'
  },
  { permission: 'view_permission', description: 'Can view permission' },
  {
    permission: 'can_view_audit_logs',
    description: 'Can view the can_view_audit_logs endpoint'
  },
  {
    permission: 'can_view_max_ping_autokick',
    description: 'Can view the max autokick ping'
  },
  {
    permission: 'can_change_admin_pings_discord_webhooks_config',
    description: 'Can change Discord admin ping config'
  },
  {
    permission: 'can_clear_crcon_cache',
    description: 'Can clear the CRCON Redis cache'
  },
  {
    permission: 'can_view_queue_length',
    description: 'Can view the maximum size of the server queue'
  },
  {
    permission: 'can_change_steam_config',
    description: 'Can change steam API config'
  },
  {
    permission: 'can_unban_profanities',
    description: 'Can unban profanities (censored game chat)'
  },
  {
    permission: 'can_view_game_logs',
    description: 'Can view the get_logs endpoint (returns unparsed game logs)'
  },
  {
    permission: 'can_add_player_watch',
    description: 'Can add a watch to players'
  },
  {
    permission: 'can_view_date_scoreboard',
    description: 'Can view the date_scoreboard endpoint'
  },
  {
    permission: 'can_view_map_whitelist',
    description: 'Can view the votemap whitelist'
  },
  {
    permission: 'can_remove_perma_bans',
    description: 'Can remove permanent bans from players'
  },
  {
    permission: 'can_view_audit_discord_webhooks_config',
    description: 'Can view Discord audit config'
  },
  {
    permission: 'can_add_blacklist_records',
    description: 'Can add players to blacklists'
  },
  {
    permission: 'can_view_connection_info',
    description: "Can view CRCON's connection info"
  },
  { permission: 'delete_user', description: 'Can delete user' },
  {
    permission: 'can_view_rcon_connection_settings_config',
    description: 'Can view game server connection settings config'
  },
  {
    permission: 'can_change_blacklists',
    description: 'Can change blacklists'
  },
  {
    permission: 'view_steamplayer',
    description: 'Can view steam player'
  },
  { permission: 'change_group', description: 'Can change group' },
  {
    permission: 'can_view_historical_logs',
    description: 'Can view historical logs'
  },
  {
    permission: 'can_view_ingame_admins',
    description: 'Can view admins connected to the game server'
  },
  {
    permission: 'can_change_camera_config',
    description: 'Can change camera notification settings'
  },
  { permission: 'change_user', description: 'Can change user' },
  {
    permission: 'can_view_vip_slots',
    description: 'Can view the number of reserved VIP slots'
  },
  { permission: 'view_logentry', description: 'Can view log entry' },
  {
    permission: 'can_view_round_time_remaining',
    description: 'Can view the amount of time left in the round'
  },
  {
    permission: 'can_change_standard_punishment_messages',
    description: 'Can change shared punishment messages'
  },
  {
    permission: 'can_ban_profanities',
    description: 'Can ban profanities (censored game chat)'
  },
  {
    permission: 'can_change_log_line_discord_webhook_config',
    description: 'Can change log webhook (messages for log events) config'
  },
  {
    permission: 'can_change_game_layout',
    description: 'Can change game layout'
  },
  { permission: 'add_group', description: 'Can add group' },
  {
    permission: 'can_change_server_name_change_config',
    description: 'Can change server name change (GSP credentials!) config'
  },
  {
    permission: 'can_change_watchlist_discord_webhooks_config',
    description: 'Can change Discord player watchlist notification config'
  },
  {
    permission: 'can_change_votekick_enabled',
    description: 'Can enable/disable vote kicks'
  },
  {
    permission: 'can_remove_temp_bans',
    description: 'Can remove temporary bans from players'
  },
  { permission: 'view_group', description: 'Can view group' },
  {
    permission: 'can_add_map_to_rotation',
    description: 'Can add a map to the rotation'
  },
  {
    permission: 'can_view_profanities',
    description: 'Can view profanities (censored game chat)'
  },
  {
    permission: 'can_view_temp_bans',
    description: 'Can view temporary banned players'
  },
  {
    permission: 'can_delete_blacklists',
    description: 'Can delete blacklists'
  },
  {
    permission: 'can_view_tk_ban_on_connect_config',
    description: 'Can view team kill ban on connect config'
  },
  {
    permission: 'can_reset_votekick_threshold',
    description: 'Can reset votekick thresholds'
  },
  {
    permission: 'can_change_team_switch_cooldown',
    description: 'Can change the team switch cooldown'
  },
  {
    permission: 'can_view_server_name_change_config',
    description: 'Can view server name change (GSP credentials!) config'
  },
  {
    permission: 'view_djangoapikey',
    description: 'Can view Django API Key'
  },
  {
    permission: 'can_add_player_comments',
    description: 'Can add comments to a players profile'
  },
  {
    permission: 'can_change_profanities',
    description: 'Can add/remove profanities (censored game chat)'
  },
  { permission: 'add_contenttype', description: 'Can add content type' },
  {
    permission: 'can_view_chat_commands_config',
    description: 'Can view the chat commands config'
  },
  {
    permission: 'can_change_broadcast_message',
    description: 'Can change the broadcast message'
  },
  {
    permission: 'can_add_maps_to_rotation',
    description: 'Can add maps to the rotation'
  },
  {
    permission: 'can_change_votemap_config',
    description: 'Can change the votemap settings'
  },
  {
    permission: 'can_add_maps_to_whitelist',
    description: 'Can add multiple maps to the votemap whitelist'
  },
  {
    permission: 'can_perma_ban_players',
    description: 'Can permanently ban players'
  },
  {
    permission: 'can_change_map_shuffle_enabled',
    description: 'Can enable/disable map shuffle'
  },
  {
    permission: 'can_view_admin_pings_discord_webhooks_config',
    description: 'Can view Discord admin ping config'
  },
  {
    permission: 'can_download_vip_list',
    description: 'Can download the VIP list'
  },
  {
    permission: 'can_view_admin_ids',
    description: 'Can view the name/steam IDs/role of everyone with a HLL games erver admin role'
  },
  {
    permission: 'view_contenttype',
    description: 'Can view content type'
  },
  {
    permission: 'can_view_server_name',
    description: 'Can view the server name'
  },
  { permission: 'delete_logentry', description: 'Can delete log entry' },
  {
    permission: 'can_change_name_kick_config',
    description: 'Can change kick players for names config'
  },
  {
    permission: 'can_view_log_stream_config',
    description: 'Can view the Log Stream config'
  },
  {
    permission: 'can_change_auto_broadcast_config',
    description: 'Can change the automated broadcast settings'
  },
  {
    permission: 'can_change_autobalance_enabled',
    description: 'Can enable/disable autobalance'
  },
  {
    permission: 'can_view_chat_discord_webhooks_config',
    description: 'Can view Discord chat notification config'
  },
  {
    permission: 'can_remove_maps_from_whitelist',
    description: 'Can remove multiple maps from the votemap whitelist'
  },
  {
    permission: 'can_remove_maps_from_rotation',
    description: 'Can remove maps from the rotation'
  },
  {
    permission: 'can_view_online_console_admins',
    description: 'Can view the player name of all connected players with a HLL game server admin role'
  },
  {
    permission: 'can_view_auto_mod_level_config',
    description: 'Can view Auto Mod Level enforcement config'
  },
  {
    permission: 'can_view_message_templates',
    description: 'Can view shared message templates'
  },
  {
    permission: 'can_message_players',
    description: 'Can message players'
  },
  {
    permission: 'can_view_all_maps',
    description: 'Can view all possible maps'
  },
  { permission: 'view_user', description: 'Can view user' },
  {
    permission: 'can_change_shared_standard_messages',
    description: 'Can change the shared standard messages'
  },
  {
    permission: 'can_view_map_rotation',
    description: 'Can view the current map rotation'
  },
  {
    permission: 'can_change_chat_discord_webhooks_config',
    description: 'Can change Discord chat notification config'
  },
  {
    permission: 'delete_steamplayer',
    description: 'Can delete steam player'
  },
  {
    permission: 'can_change_scorebot_config',
    description: 'Can change scorebot config'
  },
  {
    permission: 'can_view_standard_broadcast_messages',
    description: 'Can view shared broadcast messages'
  },
  {
    permission: 'can_remove_vip',
    description: 'Can remove VIP status from players'
  },
  {
    permission: 'can_view_next_map',
    description: 'Can view the next map in the rotation'
  },
  {
    permission: 'can_view_welcome_message',
    description: 'Can view the server welcome message'
  },
  {
    permission: 'can_view_online_admins',
    description: 'Can view admins connected to CRCON'
  },
  {
    permission: 'can_change_rcon_server_settings_config',
    description: 'Can change general CRCON server settings'
  },
  {
    permission: 'can_add_message_templates',
    description: 'Can add new shared message templates'
  },
  {
    permission: 'can_toggle_services',
    description: 'Can enable/disable services (automod, etc)'
  },
  {
    permission: 'can_view_auto_mod_no_leader_config',
    description: 'Can view Auto Mod No Leader enforcement config'
  },
  {
    permission: 'can_view_blacklists',
    description: 'Can view available blacklists'
  },
  {
    permission: 'can_delete_message_templates',
    description: 'Can delete shared message templates'
  },
  {
    permission: 'delete_contenttype',
    description: 'Can delete content type'
  },
  {
    permission: 'can_add_vip',
    description: 'Can add VIP status to players'
  },
  {
    permission: 'can_view_auto_mod_solo_tank_config',
    description: 'Can view Auto Mod No Solo Tank enforcement config'
  },
  { permission: 'add_steamplayer', description: 'Can add steam player' },
  { permission: 'view_session', description: 'Can view session' },
  { permission: 'change_session', description: 'Can change session' },
  {
    permission: 'can_change_kills_discord_webhooks_config',
    description: 'Can change Discord team/teamkill notification config'
  },
  {
    permission: 'can_view_idle_autokick_time',
    description: 'Can view the idle autokick time'
  },
  {
    permission: 'can_view_player_info',
    description: 'Can view the get_player_info endpoint (Name, steam ID, country and steam bans)'
  },
  {
    permission: 'can_change_idle_autokick_time',
    description: 'Can change the idle autokick time'
  },
  {
    permission: 'can_view_autobalance_threshold',
    description: 'Can view the autobalance threshold'
  },
  {
    permission: 'can_run_raw_commands',
    description: 'Can send raw commands to the HLL game server'
  },
  {
    permission: 'can_change_auto_mod_solo_tank_config',
    description: 'Can change Auto Mod No Solo Tank enforcement config'
  },
  {
    permission: 'can_view_auto_broadcast_config',
    description: 'Can view the automated broadcast settings'
  },
  {
    permission: 'can_view_playerids',
    description: 'Can view the get_playerids endpoint (name and steam IDs of connected players)'
  },
  {
    permission: 'change_permission',
    description: 'Can change permission'
  },
  {
    permission: 'can_create_blacklists',
    description: 'Can create blacklists'
  },
  {
    permission: 'can_flag_player',
    description: 'Can add flags to players'
  },
  {
    permission: 'can_change_votekick_threshold',
    description: 'Can change vote kick thresholds'
  },
  {
    permission: 'can_view_broadcast_message',
    description: 'Can view the current broadcast message'
  },
  {
    permission: 'can_view_gamestate',
    description: 'Can view the current gamestate'
  },
  {
    permission: 'can_change_chat_commands_config',
    description: 'Can change the chat commands config'
  },
  {
    permission: 'can_view_player_profile',
    description: 'View the detailed player profile page'
  },
  {
    permission: 'can_view_perma_bans',
    description: 'Can view permanently banned players'
  },
  {
    permission: 'can_change_queue_length',
    description: 'Can change the server queue size'
  },
  {
    permission: 'can_view_detailed_players',
    description: 'Can view get_detailed_players endpoint'
  },
  {
    permission: 'can_view_votekick_autotoggle_config',
    description: 'Can view votekick settings'
  },
  { permission: 'add_user', description: 'Can add user' },
  { permission: 'can_punish_players', description: 'Can punish players' },
  {
    permission: 'can_switch_players_on_death',
    description: 'Can switch players on death'
  },
  { permission: 'change_logentry', description: 'Can change log entry' },
  {
    permission: 'can_view_player_comments',
    description: 'Can view comments added to a players profile'
  },
  {
    permission: 'can_change_auto_mod_seeding_config',
    description: 'Can change Auto Mod No Seeding enforcement config'
  },
  {
    permission: 'can_view_get_players',
    description: 'Can view get_players endpoint (name, steam ID, VIP status and sessions) for all connected players'
  },
  { permission: 'delete_session', description: 'Can delete session' },
  {
    permission: 'add_djangoapikey',
    description: 'Can add Django API Key'
  },
  {
    permission: 'can_view_steam_config',
    description: 'Can view steam API config'
  },
  {
    permission: 'can_change_welcome_message',
    description: 'Can change the welcome (rules) message'
  },
  {
    permission: 'can_upload_vip_list',
    description: 'Can upload a VIP list'
  },
  {
    permission: 'can_view_scorebot_config',
    description: 'Can view scorebot config'
  },
  {
    permission: 'can_delete_blacklist_records',
    description: 'Can delete blacklist records'
  },
  {
    permission: 'can_change_max_ping_autokick',
    description: 'Can change the max ping autokick'
  },
  {
    permission: 'can_reset_map_whitelist',
    description: 'Can reset the votemap whitelist'
  },
  {
    permission: 'can_switch_players_immediately',
    description: 'Can immediately switch players'
  },
  {
    permission: 'can_view_camera_discord_webhooks_config',
    description: 'Can view Discord admin cam notification config'
  },
  {
    permission: 'can_view_shared_standard_messages',
    description: 'Can view the shared standard messages'
  },
  {
    permission: 'can_view_name_kick_config',
    description: 'Can view kick players for names config'
  },
  {
    permission: 'can_view_player_history',
    description: 'Can view History > Players'
  },
  {
    permission: 'can_view_standard_punishment_messages',
    description: 'Can view shared punishment messages'
  },
  { permission: 'can_kick_players', description: 'Can kick players' },
  {
    permission: 'can_change_real_vip_config',
    description: 'Can change the real VIP settings'
  },
  {
    permission: 'can_view_admin_groups',
    description: 'Can view available admin roles'
  },
  {
    permission: 'can_view_kills_discord_webhooks_config',
    description: 'Can view Discord team/teamkill notification config'
  },
  {
    permission: 'change_steamplayer',
    description: 'Can change steam player'
  },
  {
    permission: 'can_view_votemap_status',
    description: 'Can view the current votemap status (votes, results, etc)'
  },
  {
    permission: 'can_add_admin_roles',
    description: 'Can add HLL game server admin roles to players'
  },
  {
    permission: 'can_change_autobalance_threshold',
    description: 'Can change the autobalance threshold'
  },
  {
    permission: 'can_change_camera_discord_webhooks_config',
    description: 'Can change Discord admin cam notification config'
  },
  {
    permission: 'can_view_log_line_discord_webhook_config',
    description: 'Can view log webhook (messages for log events) config'
  },
  {
    permission: 'can_view_other_crcon_servers',
    description: 'Can view other servers hosted in the same CRCON (forward to all servers)'
  },
  {
    permission: 'can_change_auto_settings',
    description: 'Can change auto settings'
  },
  {
    permission: 'can_view_get_status',
    description: 'Can view the get_status endpoint (server name, current map, player count)'
  },
  {
    permission: 'can_view_real_vip_config',
    description: 'Can view the real VIP settings'
  },
  {
    permission: 'can_view_recent_logs',
    description: 'Can view recent logs (Live view)'
  },
  {
    permission: 'can_view_team_objective_scores',
    description: 'Can view the number of objectives held by each team'
  },
  {
    permission: 'can_change_discord_webhooks',
    description: 'Can change configured webhooks on the settings page'
  },
  {
    permission: 'can_remove_player_watch',
    description: 'Can remove a watch from players'
  },
  {
    permission: 'delete_djangoapikey',
    description: 'Can delete Django API Key'
  },
  {
    permission: 'can_view_team_view',
    description: 'Can view get_team_view endpoint (detailed player info by team for all connected players)'
  },
  {
    permission: 'can_reset_votemap_state',
    description: 'Can reset votemap selection & votes'
  },
  {
    permission: 'can_view_current_map',
    description: 'Can view the currently playing map'
  },
  {
    permission: 'can_set_map_whitelist',
    description: 'Can set the votemap whitelist'
  },
  {
    permission: 'can_view_auto_mod_seeding_config',
    description: 'Can view Auto Mod No Seeding enforcement config'
  },
  { permission: 'delete_group', description: 'Can delete group' },
  {
    permission: 'can_view_vac_game_bans_config',
    description: 'Can view VAC/Gameban ban on connect config'
  },
  {
    permission: 'can_change_vac_game_bans_config',
    description: 'Can change VAC/Gameban ban on connect config'
  },
  {
    permission: 'can_view_watchlist_discord_webhooks_config',
    description: 'Can view Discord player watchlist notification config'
  },
  {
    permission: 'can_view_camera_config',
    description: 'Can view camera notification settings'
  },
  {
    permission: 'can_view_player_bans',
    description: 'Can view all bans (temp/permanent) for a specific player'
  },
  {
    permission: 'change_djangoapikey',
    description: 'Can change Django API Key'
  },
  {
    permission: 'can_view_available_services',
    description: 'Can view services (automod, etc)'
  },
  {
    permission: 'can_view_map_shuffle_enabled',
    description: 'Can view if map shuffle is enabled'
  },
  {
    permission: 'delete_permission',
    description: 'Can delete permission'
  },
  { permission: 'add_session', description: 'Can add session' },
  { permission: 'add_permission', description: 'Can add permission' },
  {
    permission: 'can_change_standard_broadcast_messages',
    description: 'Can change shared broadcast messages'
  },
  {
    permission: 'can_view_discord_webhooks',
    description: 'Can view configured webhooks on the settings page'
  },
  {
    permission: 'can_change_rcon_connection_settings_config',
    description: 'Can change game server connection settings config'
  },
  {
    permission: 'can_view_detailed_player_info',
    description: 'Can view detailed player info (name, steam ID, loadout, squad, etc.)'
  },
  {
    permission: 'can_view_current_map_sequence',
    description: 'Can view the current map shuffle sequence'
  },
  {
    permission: 'can_change_audit_discord_webhooks_config',
    description: 'Can change Discord audit config'
  },
  {
    permission: 'can_view_audit_logs_autocomplete',
    description: 'Can view the get_audit_logs_autocomplete endpoint'
  },
  {
    permission: 'can_view_players',
    description: 'Can view get_players_fast endpoint for all connected players '
  },
  {
    permission: 'can_change_votekick_autotoggle_config',
    description: 'Can change votekick settings'
  },
  {
    permission: 'can_remove_all_vips',
    description: 'Can remove all VIPs'
  }
]
