const TeamBalanceAutoMod = `
        {
            /*
                Team Balance Auto Mod

                At the END of a match, if the match was a "steamroll", this automod
                moves whole squads between teams to rebalance them.

                A steamroll is defined by match DURATION (fast matches) or repeated
                same-team wins - NEVER by the score margin. A long, decisive win
                (e.g. a 60 minute 5-0) is a grind, not a steamroll.

                Armor squads are balanced as their own category (equalize armor squad
                count first). Infantry squads are then balanced by headcount and a
                combat-effectiveness score. Commander squads are never moved, and
                Recon squads are protected by default.
            */
            "enabled": false,

            /*
                If set to true, nothing is actually switched. The automod only logs
                what it WOULD do to your Discord audit log webhook.
            */
            "dry_run": false,

            /*
                Discord Webhook URL where audit logs should be sent.
            */
            "discord_webhook_url": null,

            /* --- Steamroll trigger (duration based, never margin based) --- */

            /*
                A match that ended in fewer minutes than this is treated as a
                steamroll. This is the primary, most reliable signal.
            */
            "fast_match_minutes": 30,

            /*
                Trigger when the SAME effective team has won this many matches in a row.
                Because teams swap sides every match, the same group winning repeatedly
                shows up as the raw winner (Allies/Axis) alternating - this is handled
                automatically.
                - set to 0 to disable the streak trigger.
            */
            "win_streak_threshold": 3,

            /* --- Seeding guard --- */

            /*
                Never rebalance while the server is still seeding.
            */
            "skip_when_seeding": true,

            /*
                Population at or below this number is considered "seeding" and skipped.
            */
            "seeding_player_threshold": 50,

            /* --- Armor category (evaluated separately) --- */

            /*
                Balance armor squads as their own category before infantry.
            */
            "balance_armor": true,

            /*
                Allowed difference in the NUMBER of armor squads between teams.
                - set to 0 to require equal armor squad counts.
            */
            "max_armor_squad_delta": 0,

            /*
                Maximum acceptable armor combat-effectiveness gap between teams.
                When greater than 0, an armor score gap above this value ALSO triggers
                armor balancing (needs room in "max_armor_squad_delta" to actually move).
                - set to 0 to balance armor by squad count only.
            */
            "armor_score_gap_threshold": 0,

            /* --- Infantry / headcount balance --- */

            /*
                Do nothing unless at least this many players are online.
            */
            "min_players_for_balance": 40,

            /*
                Allowed difference in team headcount after balancing.
            */
            "max_players_per_team_delta": 2,

            /*
                Maximum acceptable INFANTRY combat-effectiveness gap between teams.
                - set to 0 to always try to close the gap.
            */
            "score_gap_threshold": 0,

            /*
                Weights used to compute a squad's combat-effectiveness score:
                score = combat*w_combat + offense*w_offense + defense*w_defense + support*w_support
            */
            "weight_combat": 1.0,
            "weight_offense": 1.0,
            "weight_defense": 1.0,
            "weight_support": 1.0,

            /*
                Never move Recon squads (Commander is always excluded).
            */
            "exclude_recon": true,

            /*
                Cap on the total number of players moved per match.
                - set to 0 for no cap.
            */
            "max_players_to_switch": 0,

            /*
                Message sent to players who are switched.
            */
            "switch_message": "You have been switched to balance the teams after a steamroll.\\n\\nYour whole squad was moved together. Thanks for helping keep the match fair!"
        }
    `

    export default TeamBalanceAutoMod;
