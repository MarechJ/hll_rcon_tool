const RconConnectionNotes = `
    {
        /*
            The number of concurrent connections to the game server CRCON will open for each
            worker you've set in your .env (NB_API_WORKERS).
            This affects things like the game view that uses multiple connections to pull
            information faster so it's less likely to be out of date.
            Unless you're having issues that would be fixed by a reduced pool size
            (for instance connections being refused/timed out by your GSP) you should
            leave this at the default, 10-20 is a good range but if you reduce it below ~4
            you should not use the game view, squad automod, etc. as it will be very delayed.
            The higher the number the longer it will take for the RCON backend to start.
            This must be an integer 1 <= x <= 100
        */
        "thread_pool_size": 6,
        
        /* The maximum number of active connections that the CRCON will use to run any sort of command. */
        "max_open": 20,
        
        /* The maximum number of idle connections that the CRCON will keep before starting to close them. */
        "max_idle": 20
    }
    `

export default RconConnectionNotes