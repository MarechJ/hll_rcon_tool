const VacBansNotes = `
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

    export default VacBansNotes;