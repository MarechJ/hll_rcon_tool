const killWebhooksNotes = `
{
    /*
        A list of Discord webhook URLs to send kill/team kill messages to

        You can set as many URLs as you want, but these are updated sequentially not concurrently,
        so setting more than one will delay the updates of each one and you should probably not
        set more than a few
    */
    "hooks": [
        {
            "url": "https://discord.com/api/webhooks/.../..."
        }
    ],
    "send_kills": false,
    "send_team_kills": true
}
`

export default killWebhooksNotes
