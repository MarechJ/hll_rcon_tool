const auditWebhooksNotes = `
{
    /* 
        A list of Discord webhook URLs to send audit messages to, it's recommended to set this,
        so that kicks, bans, map changes, etc. will be shown in Discord

        You can set as many URLs as you want, but these are updated sequentially not concurrently,
        so setting more than one will delay the updates of each one and you should probably not
        set more than a few
    */
    "hooks": [
        {
            "url": "https://discord.com/api/webhooks/.../..."
        }
    ]
}
`

export default auditWebhooksNotes
