const logLineWebhooksNotes = `
{
    /*
        You can use this feature to subscribe to arbitrary log types and send them
        to Discord with optional messages.

        For example, you could mention roles or users in Discord when a match starts or ends.

        You can set as many URLs as you want, but these are updated sequentially not concurrently,
        so setting more than one will delay the updates of each one and you should probably not
        set more than a few
    */
    "webhooks": [
        /*
            A list of objects, each one can trigger off one or more log types,
            and has a webhook and optional user/role IDs to mention
        */
        {
            /* A list of log types to send to Discord */
            "log_types": [
                "CHAT[Axis][Unit]",
                "MATCH ENDED"
            ],
            "webhook": {
                "url": "https://discord.com/api/webhooks/.../...",
                /* A list of user ID(s), must be in the <@...> format to mention*/
                "user_mentions": [
                    "<@432>",
                    "<@4321>"
                ],
                /* A list of role ID(s), must be in the <@...> format  to mention*/
                "role_mentions": []
            }
        }
    ]
}
`

export default logLineWebhooksNotes
