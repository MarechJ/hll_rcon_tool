const adminPingWebhooksNotes = `
{
    /* 
        A list of Discord webhook URLs and user/role IDs to mention when one of \`trigger_words\` is used in game chat

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
    ],
    /*
        Comma-separated list of trigger words. Case-insensitive. Trigger words match whole words.
        "this is a TeSt message" would match trigger word "test"
        "this is a testmessage" would NOT match trigger word "test"
    */
    "trigger_words": [
        "!admin"
    ]
}
`;

export default adminPingWebhooksNotes;
