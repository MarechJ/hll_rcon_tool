const NoLeaderAutoMod = `
        {
            /*
                This automod has 4 steps :
                - 1. internally noting (X times) ;
                - 2. warning via direct message (Y times) ;
                - 3. punish (Z times) ;
                - 4. kick

                Note :
                The state cycle for a given squad only resets once it finally has an officer.
                So, for example, if you disabled the kick and have 3 punishes configured,
                once the 3 punishes are through, that's it : nothing will happen anymore for that squad,
                even if they still don't have an officer.

                Note 2:
                notes, warnings, punishes and kicks are tracked per player, not at the squad level.
                So if a player joins a squad that already received 3 punishes and will be kicked next,
                the new player will start at the first punish (so he won't be kick).
            */
            "enabled": false,

            /*
                If this is set to true, NO warning / punish / kick will be applied for real.
                It turns the code into a "simulation" mode
                and only send what it would do to your Discord audit log webhook.
            */
            "dry_run": false,

            /*
                Discord Webhook URL where audit logs should be sent.
            */
            "discord_webhook_url": null,

            /*
                This is either an empty list [], or a list of flags
                to exempt a player from this automod features.
                To use, add a flag or multiple flags to the list,
                then flag the players you want to exempt in the CRCON UI.
            */
            "whitelist_flags": [
                "🚨"
            ],

            /*
                Roles that are immune to punishes and kicks
                (this must be a list, the syntax is important)
                Available roles are : 'armycommander', 'officer', 'rifleman', 'assault',
                'automaticrifleman', 'medic', 'support', 'heavymachinegunner', 'antitank',
                'engineer', 'tankcommander', 'crewman', 'spotter', 'sniper'

                Example :
                    "immune_roles": [
                        "armycommander",
                        "medic"
                    ],
            */
            "immune_roles": [],

            /*
                If the player's level is below this number,
                he/she will be immune to punishes and kicks.
                - set to 0 to disable.
            */
            "immune_player_level": 0,

            /*
                If the "enabled" parameter above is set to "true",
                the automod won't do anythying below this number of players on the server.
                - set to 0 if you want the automod to be always active,
                regardless the number of players.
            */
            "dont_do_anything_below_this_number_of_players": 0,

            /*
                Step 1 of 4
                If a squad has no officer all members are noted internally but no action is taken.
                Since we sometimes receive wrong data from the game server, we note those players
                and see if these squads still don't have an officer the next time we check.
                - set to 0 to disable (it will directly move to warn) ;
                - set to 1 to X to note the squad X times before moving to the warning step.
                Recommended : 1
            */
            "number_of_notes": 1,

            /*
                This is the number of seconds to wait until moving to the next note
                (or to the warning step if 'number_of_notes' is reached).
                Recommended : 10
            */
            "notes_interval_seconds": 10,

            /*
                Step 2 of 4
                Send a direct warning message to the squads that don't have an officer.
                - set to 0 to disable (directly move to punish step) ;
                - set to -1 for infinite warnings (will never go to punish step) ;
                - set to 1 or Y to warn squad Y times before moving to punish step.
                Recommended : 2
            */
            "number_of_warnings": 2,

            /*
                This is the number of seconds until moving to the next warning
                (or to the punish step if 'number_of_warnings' is reached).
                Recommended : 60
            */
            "warning_interval_seconds": 60,

            /*
                The following variables are available :
                - {player_name} ;
                - {squad_name} ;
                - {received_warnings} ;
                - {max_warnings} ;
                - {next_check_seconds}.
            */
            "warning_message": "Warning, {player_name}! Your squad ({squad_name}) does not have an officer. Players of squads without an officer will be punished after {max_warnings} warnings (you already received {received_warnings}), then kicked.\\nNext check will happen automatically in {next_check_seconds}s.",
        
            /*
                Step 3 of 4
                Starts punishing if the squad still doesn't have an officer
                after 'number_of_warnings' * 'warning_interval_seconds'
                - set to 0 to disable to punish entirely ;
                - set to -1 for infinite punish (will never go to kick step) ;
                - set to Z to apply Z punishes before moving to kick step.
                Recommended : 2
                Advice : set 'number_of_warnings' to -1 if you set this to 0.
            */
            "number_of_punishments": 2,

            /*
                Disable the punishes until the squad has at least this number of players.
                ie : if you set 3, a squad of 2 will be immune to punishes (and kicks).
            */
            "min_squad_players_for_punish": 0,
        
            /*
                This option is the same as above, but for the entire server.
                If the server has less players than the number you set below,
                no punishes / kicks will be applied.
            */
            "min_server_players_for_punish": 0,

            /*
                This is the number of seconds to wait between punishes.
                Recommended : 60
            */
            "punish_interval_seconds": 60,

            /*
                The following variables are available :
                - {player_name} ;
                - {squad_name} ;
                - {received_punishes} ;
                - {max_punishes} ;
                - {next_check_seconds}.
            */
            "punish_message": "Your squad ({squad_name}) must have an officer.\\nYou're being punished by a bot ({received_punishes}/{max_punishes}).\\nNext check in {next_check_seconds} seconds",

            /*
                Step 4 of 4
                Note :
                If you have set 'number_of_punishments' to -1 or 0,
                it will never reach that step.
                - set to 'false' if you don't want to kick players after they reached 'number_of_punishments'.
                Advice : set 'number_of_punishments' to -1 if you set this to 'false'.
            */
            "kick_after_max_punish": true,

            /*
                Same behavior as for the punishes :
                kick is disabled if the squad has less players than this.
                ie : if you set 3, a squad of 2 will be immune to kicks.
            */
            "min_squad_players_for_kick": 0,
        
            /*
                Same behavior as for the punishes :
                kick step is disabled if the server has less players than this.
            */
            "min_server_players_for_kick": 0,

            /*
                Number of seconds to wait before kicking,
                after 'number_of_punishments' has been reached
            */
            "kick_grace_period_seconds": 60,
        
            /*
                The following variables are available :
                - {player_name} ;
                - {squad_name} ;
                - {kick_grace_period}.
            */
            "kick_message": "Your Squad ({squad_name}) must have an officer.\\nYour grace period of {kick_grace_period}s has passed.\\nYou failed to comply with the previous warnings.",
        }
    `

export default NoLeaderAutoMod
