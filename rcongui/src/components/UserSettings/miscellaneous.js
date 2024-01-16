import React from "react";
import UserSetting from ".";

export const TriggerWords = ({
  description,
  getEndpoint,
  setEndpoint,
  validateEndpoint,
  describeEndpoint,
}) => {
  const notes = ``;

  return (
    <UserSetting
      description={description}
      getEndpoint={getEndpoint}
      setEndpoint={setEndpoint}
      validateEndpoint={validateEndpoint}
      describeEndpoint={describeEndpoint}
      notes={notes}
    />
  );
};

export const RconConnectionSettings = ({
  description,
  getEndpoint,
  setEndpoint,
  validateEndpoint,
  describeEndpoint,
}) => {
  const notes = `
    {
        /*
            The number of concurrent connections to the game server CRCON will open for each
            worker you've set in your .env (NB_API_WORKERS).
            This affects things like the game view that uses multiple connections to pull
            information faster so it's less likely to be out of date.
            Unless you're having issues that would be fixed by a reduced pool size
            (for instance connections being refused/timed out by your GSP) you should
            leave this at the default, 10-20 is a good range but if you reduce it below ~4
            you should not use the game view, squad automod, etc. as it will be very delayed.
            The higher the number the longer it will take for the RCON backend to start.
            This must be an integer 1 <= x <= 100
        */
        "thread_pool_size": 6,
        
        /* The maximum number of active connections that the CRCON will use to run any sort of command. */
        "max_open": 20,
        
        /* The maximum number of idle connections that the CRCON will keep before starting to close them. */
        "max_idle": 20
    }
    `;

  return (
    <UserSetting
      description={description}
      getEndpoint={getEndpoint}
      setEndpoint={setEndpoint}
      validateEndpoint={validateEndpoint}
      describeEndpoint={describeEndpoint}
      notes={notes}
    />
  );
};

export const RconServerSettings = ({
  description,
  getEndpoint,
  setEndpoint,
  validateEndpoint,
  describeEndpoint,
}) => {
  const notes = `
    {
        /*
            This will be used for the page title of the web page and in the audit log, amongst other things.
            Keep it unique per instance
        */
        "short_name": "MyServer1",

        /*
            You must configure this to match the URL you're hosting CRCON on, or you will be unable to access the admin site due to CSRF errors
            you need to match scheme (http/https) hostname (ip, or URL) and port (8010, etc)
            if you are hosting using a domain name (example.com) you most likely do not need to include the port
            For example if you are hosting using HTTPS on example.com you would set:
            "server_url": "https://example.com"
            For example if you are hosting using HTTP on 127.0.0.1 on port 8010 you would set:
            "server_url": "http://127.0.0.1:8010"

            You can likely just copy the URL from the browser you're using to connect to CRCON
        */
        "server_url": null,

        /*
            If you set this to true your public website for stats won't work anymore
            This will request a login for all the stats endpoints
        */
        "lock_stats_api": false,

        /* If you unban a player (temp or perma) it will also remove their blacklist (if any) */
        "unban_does_unblacklist": true,

        /* Same as above but the other way around, remove a player from the blacklist will unban him */
        "unblacklist_does_unban": true,
        
        /*
            This option when turned on will forward your temp ban to all your servers
            When it is off the temp ban is only applied on the server where the command was received
        */
        "broadcast_temp_bans": true,

        /*
            This option when turned on will forward the unban to all your servers
            When is off unbanning a player will only apply on the server where the command was received
        */
        "broadcast_unbans": true,

        /*
            A stats refresh is quite intensive on CPU, disk I/O and bandwidth,
            smaller machines should choose at the very least 30 seconds, if not 60 to 120
            The below is to compute live stats based on session (from the last connection) accross all games
        */
        "live_stats_refresh_seconds": 15,

        /*
            The below is to compute live stats for the current game and starts at the begining of the game, even if the
            player disconnect and reconnected multiple times, all his/her stats are counted
        */
        "live_stats_refresh_current_game_seconds": 5

        /* This allows you to automatically action players with names that case RCON bugs */
        "invalid_names": {
          "enabled": false,
          /* 
            null: Do nothing
            "warn": Message the player when they connect
            "kick": Kick the player from the server
            "ban": Temporarily ban the player
          */
          "action": null,

          /* The message used when actioning a player whose name ends in white space */
          "whitespace_name_player_message": "Your name ends in whitespace (or has whitespace in the 20th character)\\n\\nBecause of a bug in the game admin tools this server uses will not work properly,\\nyou might suffer auto-moderation actions as a false-positive.\\n\\nPlease change your name in Steam and restart your game to avoid this.\\n\\nPlease ask T17 to prioritize fixing this bug.",
          
          /* The message used when actioning a player whose name is incorrectly shortened by the game server */
          "pineapple_name_player_message": "Your name has a special character around the 20th character (because it is truncated as it is too long)\\n\\nBecause of a bug in the game, admin tools this server uses will not work properly.\\n\\nPlease change your name in Steam and restart your game to avoid this.\\n\\nPlease ask T17 to prioritize fixing this bug.",
          
          /* The message sent to the discord audit log, {name} {steam_id_64} and {action} are valid message variables */
          "audit_message": "Player with an invalid name (ends in whitespace or a partial character when truncated) joined: {name} ({steam_id_64}\\nThis will cause errors with various auto mods (no leader, etc) and the \`playerinfo\` RCON command will not work.\\nThe player will show as 'unassigned' in Gameview.\\nAction taken = {action}",
          
          /* Due to a bug with how the kick command works, if a player can't be kicked they'll be removed by temporarily banning them, {name} {steam_id_64} and {action} are valid message variables */
          "audit_kick_unban_message": "Unbanning {name} ({steam_id_64}) that was temp banned since the \`kick\` command will not work with their name",
          "audit_message_author": "CRCON",
          
          /* The length in hours if a player is temporarily banned */
          "ban_length_hours": 1
        },

        /* This allows you to automatically action windows store players when they connect if your GSP is not updated to allow you to edit your Server.ini file */
        "windows_store_players": {
          "enabled": false,
          
          /*
            null: Do nothing
            "kick": Kick the player from the server
            "temp ban": Temporarily ban the player
            "perma ban": Permanently ban the player
          */
          "action": null,

          /* The message used when actioning a player */
          "player_message": "Windows store players are not allowed on this server.",
          
          /* The message sent to the discord audit log, {name} {steam_id_64} and {action} are valid message variables */
          "audit_message": "Windows store player {name} ({steam_id_64} connected, action taken = {action})",
          "audit_message_author": "CRCON",

          /* The length in hours if a player is temporarily banned */
          "temp_ban_length_hours": 1
        }
    }
    `;

  return (
    <UserSetting
      description={description}
      getEndpoint={getEndpoint}
      setEndpoint={setEndpoint}
      validateEndpoint={validateEndpoint}
      describeEndpoint={describeEndpoint}
      notes={notes}
    />
  );
};

export const Scorebot = ({
  description,
  getEndpoint,
  setEndpoint,
  validateEndpoint,
  describeEndpoint,
}) => {
  const notes = `
    {
        /*
            Here you can change the text scorebot displays in Discord, as well as set mandatory things like your server URL and webhook URL(s)
        */

        "all_stats_text": "All stats on: ",
        "author_name_text": "STATS LIVE HLL FRANCE - click here",
        "author_icon_url": "https://static.wixstatic.com/media/da3421_111b24ae66f64f73aa94efeb80b08f58~mv2.png/v1/fit/w_2500,h_1330,al_c/da3421_111b24ae66f64f73aa94efeb80b08f58~mv2.png",
        
        /*
            The number of top players to display from 1 to 100
            Discord has an inherent 6,000 character limit on Discord embeds
            If you set this to a large number you can easily exceed this limit
        */
        "top_limit": 10,
        "footer_icon_url": "https://static.wixstatic.com/media/da3421_111b24ae66f64f73aa94efeb80b08f58~mv2.png/v1/fit/w_2500,h_1330,al_c/da3421_111b24ae66f64f73aa94efeb80b08f58~mv2.png",
        "no_stats_available_text": "No stats recorded for that game yet",
        "find_past_stats_text": "Stats of past games on: ",
        "next_map_text": "Next map",
        "vote_text": "vote(s)",
        "players_text": "players",
        "elapsed_time_text": "Elapsed game time: ",
        "allied_players_text": "Allied Players",
        "axis_players_text": "Axis Players",
        "match_score_title_text": "Match Score",
        "match_score_text": "Allied {0} : Axis {1}",
        "time_remaining_text": "Time Remaining",
        
        /*
            A list of which stats to display, \`type\` must be one of:
                'TOP_KILLERS','TOP_RATIO','TOP_PERFORMANCE','TRY_HARDERS','TOP_STAMINA','TOP_KILL_STREAK','MOST_PATIENT',
                'I_NEVER_GIVE_UP','IM_CLUMSY','I_NEED_GLASSES','I_LOVE_VOTING','WHAT_IS_A_BREAK','SURVIVORS' or 'U_R_STILL_A_MAN'
            Discord markup is supported in \`display_format\`, you can add emoji too, do \<the emoji> on your discord to get that id
        */
        "stats_to_display": [
            {
                "type": "TOP_KILLERS",
                "display_format": ":knife: TOP KILLERS\\n*kills* <=HLLBomb=868256234439073802>"
            },
            {
                "type": "TOP_RATIO",
                "display_format": "TOP RATIO\\n*kills/death*"
            },
            {
                "type": "TOP_PERFORMANCE",
                "display_format": "TOP PERFORMANCE\\n*kills/minute*"
            },
            {
                "type": "TRY_HARDERS",
                "display_format": "TRY HARDERS\\n*deaths/minute*"
            },
            {
                "type": "TOP_STAMINA",
                "display_format": "TOP STAMINA\\n*deaths*"
            },
            {
                "type": "TOP_KILL_STREAK",
                "display_format": "TOP KILL STREAK\\n*kill streak*"
            },
            {
                "type": "MOST_PATIENT",
                "display_format": "MOST PATIENT\\n*death by teamkill*"
            },
            {
                "type": "I_NEVER_GIVE_UP",
                "display_format": "I NEVER GIVE UP\\n*death streak*"
            },
            {
                "type": "IM_CLUMSY",
                "display_format": "YES I'M CLUMSY\\n*teamkills*"
            },
            {
                "type": "I_NEED_GLASSES",
                "display_format": "I NEED GLASSES\\n*teamkill streak*"
            },
            {
                "type": "I_LOVE_VOTING",
                "display_format": "I ❤ VOTING\\n*num. votes started*"
            },
            {
                "type": "WHAT_IS_A_BREAK",
                "display_format": "WHAT IS A BREAK?\\n*ingame time*"
            },
            {
                "type": "SURVIVORS",
                "display_format": "SURVIVORS\\n*longest life (min.)*"
            },
            {
                "type": "U_R_STILL_A_MAN",
                "display_format": "U'R STILL A MAN\\n*shortest life (min.)*"
            }
        ],

        /*
            The URL you use to connect to your CRCON
        */
        "base_api_url": "http://localhost:8010/",

        /*
            The URL you use to connect to your public stats site
        */
        "base_scoreboard_url": "http://localhost:7010/",

        /*
            You can set as many URLs as you want, but these are updated sequentially not concurrently,
            so setting more than one will delay the updates of each one and you should probably not
            set more than one or two
        */
        "webhook_urls": [
            "https://discord.com/api/webhooks/.../..."
        ]
    }
    `;

  return (
    <UserSetting
      description={description}
      getEndpoint={getEndpoint}
      setEndpoint={setEndpoint}
      validateEndpoint={validateEndpoint}
      describeEndpoint={describeEndpoint}
      notes={notes}
    />
  );
};

export const SteamAPI = ({
  description,
  getEndpoint,
  setEndpoint,
  validateEndpoint,
  describeEndpoint,
}) => {
  const notes = `
    {
        /*
            The steam API is used to display country flags, VAC and game bans
            and is used for the VAC/game ban feature (if configured)
            Get a key from: https://steamcommunity.com/dev/apikey
        */
        "api_key": "your_api_key_here"
    }
    `;

  return (
    <UserSetting
      description={description}
      getEndpoint={getEndpoint}
      setEndpoint={setEndpoint}
      validateEndpoint={validateEndpoint}
      describeEndpoint={describeEndpoint}
      notes={notes}
    />
  );
};

export const VacGameBans = ({
  description,
  getEndpoint,
  setEndpoint,
  validateEndpoint,
  describeEndpoint,
}) => {
  const notes = `
    {
        /*
            You **must** have a Steam API key configured for this feature to work

            Automatically ban a player if they have a VAC or game ban within the desired timeframe
            E.g. if you set the value to 160, any players with a VAC or game ban within the
            last 160 days will be permanently banned. Setting this to 0 will disable it.
        */
        "vac_history_days": 0,

        /*
            In COMBINATION with \`vac_history_days\`, you can also ban players with game bans
            The value is the number of GAME bans a player must have to be auto-banned
            For example if you set 2, any players with 2 or more game bans will be permanently banned
            0 disables that feature (any number of game bans is allowed).
            Remember that game bans don't necessarily mean much.
        */
        "game_ban_threshhold": 0,

        /*
            The reason to the player for the permanent ban. You may use the below variables within your reason
            {DAYS_SINCE_LAST_BAN}
            {MAX_DAYS_SINCE_BAN}
        */
        "ban_on_vac_history_reason": "VAC/Game ban history ({DAYS_SINCE_LAST_BAN} days ago)",
        
        /*
            This is either an empty list [] or a list of flags to exempt a player
            from the VAC/Game Ban feature.
            To use, add a flag or multiple flags to the list, and then flag
            the players you want to exempt in the CRCON UI with one of those flags
            If they have already been banned you will need to clear the bans for them to be able to connect
        */
        "whitelist_flags": [
            "🤡"
        ]
    }
    `;

  return (
    <UserSetting
      description={description}
      getEndpoint={getEndpoint}
      setEndpoint={setEndpoint}
      validateEndpoint={validateEndpoint}
      describeEndpoint={describeEndpoint}
      notes={notes}
    />
  );
};

export const TeamKillBanOnConnect = ({
  description,
  getEndpoint,
  setEndpoint,
  validateEndpoint,
  describeEndpoint,
}) => {
  const notes = `
    {
        "enabled": false,
        "message": "Your first action on the server was a TEAM KILL you were banned as a result",
        "author_name": "HATERS GONNA HATE",
        
        /*
            Exlude TK with certain weapons from triggering the ban, weapon names can be found at: https://gist.github.com/timraay/5634d85eab552b5dfafb9fd61273dc52#available-weapons
        */
        "excluded_weapons": [
            "155MM HOWITZER [M114]"
        ],

        /* TK after connect only counts as an offense for the first N minute after connecting, N is the number you set below */
        "max_time_after_connect_minutes": 5,
        
        /* A TK after connecting will be ignored if there's N kills before it */
        "ignore_tk_after_n_kills": 1,
        
        /* A TK after connecting will be ignored if there's <N> death before it */
        "ignore_tk_after_n_deaths": 2,
        
        /* If any of the conditions below are true the player won't be inspected upon TK */
        "whitelist_players": {
            /* To use, add a flag or multiple flags to the list, and then flag the players you want to exempt in the CRCON UI with one of those flags */
            "has_flag": [],
            "is_vip": true,
            /* Set to 0 for infinite */
            "has_at_least_n_sessions": 10
        },

        /* The maximum amount of TK tolerated after connecting, TK get counted if it wasn't excluded by any of the parameters above */
        "teamkill_tolerance_count": 1,
        
        /* If left unset, the webhook defaults to your audit log webhook */
        "discord_webhook_url": null,
        "discord_webhook_message": "{player} banned for TK right after connecting"
    }
    `;

  return (
    <UserSetting
      description={description}
      getEndpoint={getEndpoint}
      setEndpoint={setEndpoint}
      validateEndpoint={validateEndpoint}
      describeEndpoint={describeEndpoint}
      notes={notes}
    />
  );
};

export const NameKicks = ({
  description,
  getEndpoint,
  setEndpoint,
  validateEndpoint,
  describeEndpoint,
}) => {
  const notes = `
    {
        /*
            A list of regular expressions player names are tested against when they join,
            any player name that matches any of the regular expressions will be kicked
            
            You can test your regex here: https://regex101.com/ (set the type to "Python")
        */

        /*
          You must escape any \ character in your regular expressions
          For example:
            ^[\\d]+$ is correct
            ^[\d]+$ is not correct and will cause JSON parsing errors
        */
        "regular_expressions": [],

        "kick_reason": "Your nickname is invalid",

        /* If left unset, the webhook default to your audit log webhook */
        "discord_webhook_url": null,

        /*
            This is either an empty list [] or a list of flags to exempt a player
            from the name kick feature.
            To use, add a flag or multiple flags to the list, and then flag
            the players you want to exempt in the CRCON UI with one of those flags
        */
        "whitelist_flags": []
    }
    `;

  return (
    <UserSetting
      description={description}
      getEndpoint={getEndpoint}
      setEndpoint={setEndpoint}
      validateEndpoint={validateEndpoint}
      describeEndpoint={describeEndpoint}
      notes={notes}
    />
  );
};

export const ExpiredVIP = ({
  description,
  getEndpoint,
  setEndpoint,
  validateEndpoint,
  describeEndpoint,
}) => {
  const notes = `
    {
        /*
            This feature removes VIP from players when their expiration date is less than the present time
            Regardless of whether or not you add an expiration date to a player, this feature must be turned on
            and the service running for VIP to be removed
        */
        "enabled": true,

        /* The number of minutes between checking for expired VIPs to prune*/
        "interval_minutes": 60,

        /* If left unset, the webhook defaults to your audit log webhook */      
        "discord_webhook_url": null
    }
    `;

  return (
    <UserSetting
      description={description}
      getEndpoint={getEndpoint}
      setEndpoint={setEndpoint}
      validateEndpoint={validateEndpoint}
      describeEndpoint={describeEndpoint}
      notes={notes}
    />
  );
};

export const GTXNameChange = ({
  description,
  getEndpoint,
  setEndpoint,
  validateEndpoint,
  describeEndpoint,
}) => {
  const notes = `
    {
        /*
            This feature allows servers hosted by GTX to change their server name without restarting the
            game server, or having to do it through their game server panel.

            Your IP and SFTP port can be found in your game server panel.

            The GSP username/password must be set in your .env
        */

        /* This is the IP address of your game server */
        "ip": "127.0.0.1",

        /* This is the SFTP port for your game server */
        "port": 9933
          
    }
    `;

  return (
    <UserSetting
      description={description}
      getEndpoint={getEndpoint}
      setEndpoint={setEndpoint}
      validateEndpoint={validateEndpoint}
      describeEndpoint={describeEndpoint}
      notes={notes}
    />
  );
};
