const TkBansNotes =`
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
    `

export default TkBansNotes;