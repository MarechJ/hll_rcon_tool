# hll_rcon_tool
Hell let loose RCON bindings in pythoin with CLI and soon http API + react gui with extended command and state.


## USAGE with docker

   # Build the image
   $ docker build . -t rcon

   # Set you server info as environement variables and run the cli
   $ docker run -it -e HLL_HOST=1.1.1.1 -e HLL_PORT=20300 -e HLL_PASSWORD=mypassword rcon python -m rcon.cli
     
     Usage: cli.py [OPTIONS] COMMAND [ARGS]...

     Options:
       --help  Show this message and exit.

     Commands:
       get_admin_ids
       get_autobalance_threshold
       get_logs
       get_map
       get_map_rotation
       get_name
       get_permabans
       get_players
       get_team_switch_cooldown
       get_temp_bans
       set_broadcast
       set_map
       set_welcome_message
       ...

    $ docker run -it -e HLL_HOST=1.1.1.1 -e HLL_PORT=20300 -e HLL_PASSWORD=mypassword rcon python -m rcon.cli get_name

      [FR]-[CFr]CorpsFranc https://discordapp.com/invite/wX2K2uG


