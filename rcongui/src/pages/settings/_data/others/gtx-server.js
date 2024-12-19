const gtxServerNotes = `
    {
        /*
            This feature allows servers hosted by GTX to change their server name without restarting the
            game server, or having to do it through their game server panel.

            Your IP and SFTP port can be found in your game server panel.

            The GSP username/password must be set in your .env
        */

        /* This is the IP address of your game server */
        "ip": "127.0.0.1",

        /* This is the SFTP port for your game server */
        "port": 9933
          
    }
    `

export default gtxServerNotes
