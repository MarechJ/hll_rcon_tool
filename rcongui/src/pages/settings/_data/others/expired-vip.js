const expiredVipNotes = `
    {
        /*
            This feature removes VIP from players when their expiration date is less than the present time
            Regardless of whether or not you add an expiration date to a player, this feature must be turned on
            and the service running for VIP to be removed
        */
        "enabled": true,

        /* The number of minutes between checking for expired VIPs to prune*/
        "interval_minutes": 60,

        /* If left unset, the webhook defaults to your audit log webhook */      
        "discord_webhook_url": null
    }
    `

export default expiredVipNotes
