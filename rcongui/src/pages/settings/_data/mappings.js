export const webhooks = [
  {
    path: '/settings/webhooks/audit',
    command: 'audit_discord_webhooks_config',
    name: 'Audit Webhooks'
  },
  {
    path: '/settings/webhooks/admin-ping',
    command: 'admin_pings_discord_webhooks_config',
    name: 'Admin Ping Webhooks'
  },
  {
    path: '/settings/webhooks/watchlist',
    command: 'watchlist_discord_webhooks_config',
    name: 'Watchlist Webhooks'
  },
  {
    path: '/settings/webhooks/camera',
    command: 'camera_discord_webhooks_config',
    name: 'Camera Webhooks'
  },
  {
    path: '/settings/webhooks/chat',
    command: 'chat_discord_webhooks_config',
    name: 'Chat Webhooks'
  },
  {
    path: '/settings/webhooks/kills',
    command: 'kills_discord_webhooks_config',
    name: 'Kill/Team Kill Webhooks'
  },
  {
    path: '/settings/webhooks/log-line',
    command: 'log_line_webhook_config',
    name: 'Log Line Webhooks'
  }
]

export const automods = [
  {
    path: '/settings/automods/level',
    command: 'auto_mod_level_config',
    name: 'Level Auto Mod'
  },
  {
    path: '/settings/automods/no-leader',
    command: 'auto_mod_no_leader_config',
    name: 'No Leader Auto Mod'
  },
  {
    path: '/settings/automods/seeding',
    command: 'auto_mod_seeding_config',
    name: 'Seeding Auto Mod'
  },
  {
    path: '/settings/automods/no-solo-tank',
    command: 'auto_mod_solo_tank_config',
    name: 'No Solo Tank Auto Mod'
  }
]

export const others = [
  {
    path: '/settings/others/seed-vip',
    command: 'seed_vip_config',
    name: 'Seeder VIP Reward'
  },
  {
    path: '/settings/others/game-server',
    command: 'rcon_connection_settings_config',
    name: 'Game Server Connection Settings'
  },
  {
    path: '/settings/others/crcon',
    command: 'rcon_server_settings_config',
    name: 'General CRCON Settings'
  },
  {
    path: '/settings/others/chat-commands',
    command: 'chat_commands_config',
    name: 'Chat Commands Settings'
  },
  {
    path: '/settings/others/rcon-chat-commands',
    command: 'rcon_chat_commands_config',
    name: 'RCON Chat Commands Settings'
  },
  {
    path: '/settings/others/scorebot',
    command: 'scorebot_config',
    name: 'Scorebot'
  },
  {
    path: '/settings/others/steam',
    command: 'steam_config',
    name: 'Steam API'
  },
  {
    path: '/settings/others/vac-bans',
    command: 'vac_game_bans_config',
    name: 'VAC/Game Bans'
  },
  {
    path: '/settings/others/tk-bans',
    command: 'tk_ban_on_connect_config',
    name: 'TK Ban On Connect'
  },
  {
    path: '/settings/others/name-kicks',
    command: 'name_kick_config',
    name: 'Name Kicks'
  },
  {
    path: '/settings/others/expired-vip',
    command: 'expired_vip_config',
    name: 'Expired VIP'
  },
  {
    path: '/settings/others/gtx-server',
    command: 'server_name_change_config',
    name: 'GTX Server Name Change'
  },
  {
    path: '/settings/others/log-stream',
    command: 'log_stream_config',
    name: 'Log Stream'
  }
]
