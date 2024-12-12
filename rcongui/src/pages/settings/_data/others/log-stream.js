const logStreamNotes = `
    {
        /*
            The log_stream is a Redis stream that stores logs from the game server in sequential order on a transient basis (they are not persisted to the database and are cleared on service startup) to support pushing new logs to external tools through a websocket endpoint.

            Parameters :
            - stream_size: The number of logs the stream will retain before discarding the oldest logs.
            - startup_since_mins: The number of minutes of logs to request from the game service when the service starts up
            - refresh_frequency_sec: The poll rate for asking for new logs from the game server
            - refresh_since_mins The number of minutes of logs to request from the game service each loop

            See https://github.com/MarechJ/hll_rcon_tool/wiki/Streaming-Logs for a detailed description.
        */
    }
    `;

    export default logStreamNotes;