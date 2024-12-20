const CRCONNotes = `
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
          
          /* The message sent to the discord audit log, {name} {player_id} and {action} are valid message variables */
          "audit_message": "Windows store player {name} ({player_id} connected, action taken = {action})",
          "audit_message_author": "CRCON",

          /* The length in hours if a player is temporarily banned */
          "temp_ban_length_hours": 1
        }
    }
    `

export default CRCONNotes;
