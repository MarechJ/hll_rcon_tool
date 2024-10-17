const nameKicksNotes = `
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
    `

    export default nameKicksNotes;