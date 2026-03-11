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
        
        /*
            Whether Community RCon should track performance metrics for the RCon communication, such as
            number of opened/closed connections or send commands. The metrics will be counted for the interval
            configured with performance_statistics_interval_seconds and reset every interval. You should only
            enable this when you know what you're doing.
            Changing this setting requires a restart of the supervisor and backend container.
         */
        "performance_statistics_enabled": false,
        
        /*
            The interval in seconds between Community RCon dumps the performance metrics gathered. This also defined the
            time-window in which the metrics are collected. For example:
            If configured to 30, Community RCon will collect performance metrics for 30 seconds (such as send commands
            to the game server) before dumping the result to the logs. After that a new time-window starts with all values
            set back to 0.
            Changing this setting requires a restart of the supervisor and backend container.
            
            This needs to be a multiple of 10 (10, 20, 30, 40, etc.) and cannot be smaller than 10.
         */
        "performance_statistics_interval_seconds": 30
    }
    `;

export default RconConnectionNotes
