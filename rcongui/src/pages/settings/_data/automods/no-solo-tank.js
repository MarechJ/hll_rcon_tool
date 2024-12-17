const NoSoloTankAutoMod = `
        {
            /*
                This automod has 4 steps :
                - 1. internally noting (X times) ;
                - 2. warning via direct message (Y times) ;
                - 3. punish (Z times) ;
                - 4. kick.

                Note :
                The state cycle for a given squad only resets once it finally has more than one member.
                So, for example, if you disabled the kick and have 3 punishes configured,
                once the 3 punishes are through, that's it : nothing will happen anymore for the player,
                even if he's still alone in his armor squad.
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
                If a player is solo in an armor squad, he will be noted internally but no action will be taken,
                since we sometimes receive wrong data from the game server.
                So we 'note' those players and see if they are still are solo the next time we check.
                - set to 0 to disable (this means it will move to warn directly) ;
                - set to 1 to X to note the squad X times before moving to the warn step ;
                Recommended : 0 (the squad opener will immediatly get the warning).
            */
            "number_of_notes": 0,

            /*
                This is the number of seconds to wait until moving to the next note
                (or to the warning step if 'number_of_notes' is reached).
                Recommended : 10
            */
            "notes_interval_seconds": 10,

            /*
                Step 2 of 4
                Send a direct warning message to the solo tank player.
                - set to 0 to disable (directly move to punish step) ;
                - set to -1 for infinite warnings (will never go to punish step) ;
                - set to 1 or Y to warn squad Y times before moving to punish step.
                Recommended : 2
            */
            "number_of_warnings": 2,

            /*
                This is the number of seconds to wait until moving to the next warning step
                (or to the punish step if 'number_of_warnings' is reached).
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
            "warning_message": "Warning, {player_name} !\\n\\nYou can't play solo tank on this server !\\n\\nYou will be punished after {max_warnings} warnings\\n(you already received {received_warnings})\\n\\nNext check will happen automatically in {next_check_seconds}s.",

            /*
                Step 3 of 4
                If the player is still solo in his tank
                after 'number_of_warnings' * 'warning_interval_seconds'
                - set to 0 to disable to punish entirely ;
                - set to -1 for infinite punish (will never go to kick step) ;
                - set to Z to apply Z punishes before moving to kick step.
                Recommended : 2
                Advice : set 'number_of_warnings' to -1 if you set this to 0.
            */
            "number_of_punishments": 2,

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
            "punish_message": "\\n\\nYou've been punished by a bot,\\nbecause you're playing solo in the armor squad {squad_name}.\\n\\n(Punition {received_punishes} of {max_punishes} before kick)\\n\\nNext check in {next_check_seconds}s.\\n\\n",

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
            "kick_message": "You've been kicked by a bot.\\n\\nYou were still playing solo in the armor squad {squad_name},\\n{kick_grace_period}s after being punished."
        }
    `

export default NoSoloTankAutoMod
