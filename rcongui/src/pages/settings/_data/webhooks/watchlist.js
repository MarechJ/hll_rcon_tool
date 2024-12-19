const watchlistWebhooksNotes = `
{
    /*
        A list of Discord webhook URLs and user/role IDs to mention when a watched player
        connects to the server

        You can set as many URLs as you want, but these are updated sequentially not concurrently,
        so setting more than one will delay the updates of each one and you should probably not
        set more than a few
    */
    "hooks": [
        {
            "url": "https://discord.com/api/webhooks/.../...",
            /* A list of user ID(s), must be in the <@...> format */
            "user_mentions": [
                "<@1234>"
            ],
            /* A list of role ID(s), must be in the <@&...> format */
            "role_mentions": [
                "<@&1234>"
            ]
        }
    ]
}
`

export default watchlistWebhooksNotes
