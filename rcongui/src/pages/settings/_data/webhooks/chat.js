const chatWebhooksNotes = `
{
    /*
        A list of Discord webhook URLs and user/role IDs to send in game chat to

        You can set as many URLs as you want, but these are updated sequentially not concurrently,
        so setting more than one will delay the updates of each one and you should probably not
        set more than a few
    */
    "hooks": [
        {
            "url": "https://discord.com/api/webhooks/.../..."
        }
    ],
    /* Whether or not in game chat can @ mention Discord users/roles */
    "allow_mentions": true
}
`

export default chatWebhooksNotes
