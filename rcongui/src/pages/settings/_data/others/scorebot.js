const ScorebotNotes = `
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
`

export default ScorebotNotes
