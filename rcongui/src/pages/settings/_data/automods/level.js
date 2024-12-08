const levelAutoModNotes = `
        {
            /* 
                This automod has 2 features:
                1. Global server min/max level :
                - No warning, players are kick after connection if they don't match level requirements.
                2. Min level by role (3 steps) :
                - 2.1. warning via direct message (Y times) ;
                - 2.2. punish (Z times) ;
                - 2.3. kick.

                Note :
                The state cycle for a given player only resets once the rule-violation is fixed.
                So, for example, if you disabled the kick and have 3 punishes configured,
                once the 3 punishes are through, that's it : nothing will happen anymore to the players,
                even if they still break level thresholds rules.
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
                If the "enabled" parameter above is set to "true",
                the automod won't do anythying below this number of players on the server.
                - set to 0 if you want the automod to be always active,
                regardless the number of players.
            */
            "dont_do_anything_below_this_number_of_players": 0,

            /* 
                Announce that the server has managed level thresholds
                when at least one level thresholds rule is enabled.
                This message occurs only once, when a player connects to the server.
            */
            "announcement_enabled": false,

            /*
                Only make the announce to players that are impacted by the level thresholds rules.
            */
            "only_announce_impacted_players": true,

            /*
                The following variables are available :
                - {min_level_msg} from min_level_message value ;
                - {max_level_msg} from max_level_message value ;
                - {level_thresholds_msg} from level_thresholds's message value
            */
            "announcement_message": "This server is under level thresholds control.\\n\\n{min_level_msg}{max_level_msg}{level_thresholds_msg}\\nThanks for understanding.",

            /*
                Step 1 of 3
                Send a direct warning message to the players that violate level thresholds rules.
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
            "warning_message": "Warning, {player_name}! You violate level thresholds rules on this server: {violation}\\nYou will be punished after {max_warnings} warnings (you already received {received_warnings}), then kicked.\\nNext check will happen automatically in {next_check_seconds}s.",

            /*
                Step 2 of 3
                Start punishing if the player still violates a level thresholds rule
                after 'number_of_warnings' * 'warning_interval_seconds'
                - set to 0 to disable to punish step entirely.
                - set to -1 for infinite punishes (will never go to kick step) ;
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
                - {received_punishes} ;
                - {max_punishes} ;
                - {next_check_seconds} ;
                - {violation}.
            */
            "punish_message": "You violated level thresholds rules on this server: {violation}.\\nYou're being punished by a bot ({received_punishes}/{max_punishes}).\\nNext check in {next_check_seconds} seconds",

            /*
                Step 3 of 3
                Note :
                If you have set 'number_of_punishments' to -1 or 0,
                it will never reach that step.
                - set to 'false' if you don't want to kick players after they reached 'number_of_punishments'.
                Advice : set 'number_of_punishments' to -1 if you set this to 'false'.
            */
            "kick_after_max_punish": true,

            /*
                Same behavior as for the punishes :
                if the squad has less players than this, automod won't kick.
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
                - {kick_grace_period} ;
                - {violation}.
            */
            "kick_message": "You violated level thresholds rules on this server: {violation}.\\nYour grace period of {kick_grace_period}s has passed.\\nYou failed to comply with the previous warnings.",

            /*
                This is the message that will be used in the force kick without warnings
                when player does not match global level thresholds.
                The following variables are available :
                - {player_name} ;
                - {squad_name} ;
                - {violation}.
            */
            "force_kick_message": "You violated level thresholds rules on this server: {violation}.",

            /* 
                This allows to configure a global minimum level on the whole server
                and the matching kick message to display to players.
                - set 'min_level' to 0 to disable.
            */
            "min_level": 0,
            "min_level_message": "Access to this server is not allowed under level {level}",

            /*
                This allows to configure a global maximum level on the whole server
                and the matching kick message to display to players.
                - set 'max_level' to 0 to disable.
            */
            "max_level": 0,
            "max_level_message": "Access to this server is not allowed over level {level}",

            /*
                Violation message used as a description of the level thresholds violation
                when player is messaged, punished and kicked.
                Available properties:
                - {role} matching label's value of previous map
                - {level} matching level's value from previous map.
            */
            "violation_message": "{role} are not allowed under level {level}",

            /*
                Enable ('true') or disable ('false') the protection against "level 1 bug" :
                due to a missed synchro between Steam and the game server,
                any player can log in as level 1, no matter their real level.
                They could then be punished if violating level rules.
                - set to 'true' to immune level 1 players from warn/punishes/kicks.
                Recommended : false (this bug seems to have disappeared since 2023)
            */
            "levelbug_enabled": false,

            /*
                Restricts access to roles when :
                player's level is below 'min_level' AND server's players count is >= 'min_players'.
                Available roles :
                    'armycommander', 'officer', 'antitank', 'automaticrifleman', 'assault', 'heavymachinegunner',
                    'support', 'sniper', 'spotter', 'rifleman', 'crewman', 'tankcommander', 'engineer', 'medic'.
                Label's values are the roles translations in your language.
                - To disable, leave roles's value empty. ie. "level_thresholds: {}"
                - To enable level enforcement at all times, set 'min_players' at 0.
            */
            "level_thresholds": {
                "armycommander": {
                    "label": "Commander",
                    "min_players": 0,
                    "min_level": 50
                }
            }
        }
    `

export default levelAutoModNotes;