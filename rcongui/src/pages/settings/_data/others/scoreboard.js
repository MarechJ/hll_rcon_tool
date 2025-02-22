const ScoreboardNotes = `
    {
    /*
        Here you can change the text the scoreboard displays in Discord, as well as set mandatory things like your public stats URL and webhook URL(s)
    */

        // Your public stats site
        "public_scoreboard_url": "https://beer2-stats.squidds.tv/",
        // A list of Discord webhook URLs to send updates to
        "hooks": [
            {
            "url": "https://discord.com/api/webhooks/1340770881965789236/eXbrYaKcqzPZNw06Md1v-7gZESPtnWkAPjBNo1CeKG4uHprkV22G_QZ5Tcf24KJCUtPf"
            }
        ],
        "footer_last_refreshed_text": "Last Refreshed",
        "header_gamestate_time_between_refreshes": 5,
        "server_name": true,
        "quick_connect_url": null,
        "battlemetrics_url": null,
        "show_map_image": true,
        // The format to show who holds how many objectives; you can use discord emojis, etc.
        "objective_score_format_generic": "Allied {0}: Axis {1}",
        "objective_score_format_ger_v_us": "<:icoT_US:1060219985215094804> {0} : <:icoT_GER:1060219972871278602> {1}",
        "objective_score_format_ger_v_sov": "<:icoT_RUS:1060217170455433286> {0} : <:icoT_GER:1060219972871278602> {1}",
        "objective_score_format_ger_v_uk": "<:icoT_UK:1114060867068235807> {0} : <:icoT_GER:1060219972871278602> {1}",

        /* A list of embeds to show in the header/gamestate message */
        "header_gamestate_embeds": [
            {
            "name": "# Allied Players",
            "value": "num_allied_players",
            "inline": true
            },
            {
            "name": "# Axis Players",
            "value": "num_axis_players",
            "inline": true
            },
            {
            "name": "Total Players",
            "value": "slots",
            "inline": true
            },
            {
            "name": "EMPTY",
            "value": "​",
            "inline": false
            },
            {
            "name": "# Allied VIPs",
            "value": "num_allied_vips",
            "inline": true
            },
            {
            "name": "# Axis VIPs",
            "value": "num_axis_vips",
            "inline": true
            },
            {
            "name": "EMPTY",
            "value": "​",
            "inline": false
            },
            {
            "name": "Match Score",
            "value": "score",
            "inline": true
            },
            {
            "name": "Time Remaining",
            "value": "time_remaining",
            "inline": true
            },
            {
            "name": "EMPTY",
            "value": "​",
            "inline": false
            },
            {
            "name": "Current Map",
            "value": "current_map",
            "inline": true
            },
            {
            "name": "Next Map",
            "value": "next_map",
            "inline": true
            }
        ],
        "map_rotation_time_between_refreshes": 30,
        "show_map_rotation": true,
        "current_map_format": "🟩 {1}. **{0}**",
        "next_map_format": "🟨 {1}. {0}",
        "other_map_format": "⬛ {1}. {0}",
        "show_map_legend": true,
        "map_rotation_title_text": "Map Rotation",
        "map_legend": "\nLegend\n🟩 - Current Map\n🟨 - Next Map\n⬛ - Other Maps",
        "player_stats_title_text": "Player Stats",
        "player_stats_time_between_refreshes": 5,
        "player_stats_num_to_display": 5,
        "player_stat_embeds": [
            {
            "name": ":knife: Highest Kills",
            "value": "kills",
            "inline": true
            },
            {
            "name": ":skull: Highest Deaths",
            "value": "deaths",
            "inline": true
            },
            {
            "name": "EMPTY",
            "value": "​",
            "inline": false
            },
            {
            "name": ":skull: Highest Team Kills",
            "value": "teamkills",
            "inline": true
            },
            {
            "name": ":knife: Highest KDR",
            "value": "kill_death_ratio",
            "inline": true
            },
            {
            "name": "EMPTY",
            "value": "​",
            "inline": false
            },
            {
            "name": ":knife: Kills/Minute",
            "value": "kills_per_minute",
            "inline": true
            },
            {
            "name": ":skull: Deaths/Minute",
            "value": "deaths_per_minute",
            "inline": true
            },
            {
            "name": "EMPTY",
            "value": "​",
            "inline": false
            },
            {
            "name": ":knife: Kill Streak",
            "value": "kills_streak",
            "inline": true
            },
            {
            "name": ":skull: Death Streak",
            "value": "deaths_without_kill_streak",
            "inline": true
            },
            {
            "name": "EMPTY",
            "value": "​",
            "inline": false
            },
            {
            "name": ":no_entry: Team Kill Streak",
            "value": "teamkills_streak",
            "inline": true
            },
            {
            "name": ":no_entry: Highest Team Kill Deaths",
            "value": "deaths_by_tk",
            "inline": true
            },
            {
            "name": "EMPTY",
            "value": "​",
            "inline": false
            },
            {
            "name": ":clock9: Longest Life",
            "value": "longest_life_secs",
            "inline": true
            },
            {
            "name": ":clock1: Shortest Life",
            "value": "shortest_life_secs",
            "inline": true
            },
            {
            "name": "EMPTY",
            "value": "​",
            "inline": false
            },
            {
            "name": ":clock1: In Game Time",
            "value": "time_seconds",
            "inline": true
            },
            {
            "name": "Votes Started",
            "value": "nb_vote_started",
            "inline": true
            }
        ]
}
`;

export default ScoreboardNotes;
