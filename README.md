# Hell Let Loose (HLL) advanced RCON  

CLI (Python), an HTTP API (Python) and a friendly GUI (React)

Feel free to contribute. There's some ironing out and lots of features to do :)

## How to install the APP

### With docker compose

Pre-requistes:
  - Having a dedicated server (Linux or Windows)
  - Docker Engine (Community) installed: https://docs.docker.com/install/
  - Docker Compose installed: https://docs.docker.com/compose/install/

#### Install steps

##### Get the sources

    git clone https://github.com/MarechJ/hll_rcon_tool.git
    cd hll_rcon_tool

Note: If you have several servers, clone it multiple times in different directories like so:

    git clone https://github.com/MarechJ/hll_rcon_tool.git hll_rcon_tool_server_number_2
    cd hll_rcon_tool_server_number_2

__From here all the commands assume that you are at the root of the repo you just cloned__

##### Set your server informations. Edit the .env and fill in the blanks (for all your servers) like so:


    # Ip address of the game server
    HLL_HOST=22.33.44.55
    # Rcon port (not the query one!)
    HLL_PORT=20310
    # Your rcon password
    HLL_PASSWORD=mypassword
    # Choose a password for your Database
    HLL_DB_PASSWORD=mydatabasepassword

    # If you have multiple servers, also change these lines (each server must have a different port, just increment the number)
    RCONWEB_PORT=8011
    HLL_DB_HOST_PORT=5433
    HLL_REDIS_HOST_PORT=6380


You could also just export the variables in your terminal before running the docker-compose commands
OR edit the `docker-compose.yml` and replace the `${variable}` directly in there, however you might have a conflic next time you update the sources.
Alternatively you can also specify them in the command line. More details: https://docs.docker.com/compose/environment-variables/#set-environment-variables-with-docker-compose-run

##### Create a .htpasswd to protect your RCON from the public

    mkdir pw
    cd pw
    htpasswd -c .htpasswd <username>
      New password:
      Re-type new password:
      Adding password for user <username>

Some additional info: https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-http-basic-authentication/

##### RUN it!

    docker-compose up -d 

The web application will be available on `<your server ip>:8010`
Feel free to change the port to your likings in the docker-compose.yml:

    frontend:
      build: ./rcongui
      environment:
        REACT_APP_BATTLEMETRICS_SERVERID: ${BATTLEMETRICS_SERVERID}
      ports:
        # --> here <---
        - 8010:80  

##### To update to the latest version:

    docker-compose pull && docker-compose up -d

##### To ROLLBACK (in case of issue) to a previous version:

Check the availabe versions numbers on docker hub (or github releases):
https://hub.docker.com/r/maresh/hll_rcon/tags
https://github.com/MarechJ/hll_rcon_tool/releases

Edit you docker-compose.yml and change all the images from:

    image: maresh/hll_rcon:latest
    ...
    image: maresh/hll_rcon_frontend:latest

To the version you want (here we use v1.1.0)

    image: maresh/hll_rcon:v1.1.0
    ...
    image: maresh/hll_rcon_frontend:v1.1.0


##### If you want the auto broadcasts

    # Create a file at the root of the repo
    touch broadcasts.txt
    # Edit the file to look like the below
    cat broadcasts.txt
    
    60 /nextmap
    30 This message will be displayed for 30 secs

The integer at the beginning is the time in seconds the message should be diplayed.
/nextmap is a special message that will show the next map to come
You can have as many messages as you want, they run in a loop starting from the first one.
Don't forget to add a line return after the last line


## Known issues and limitations

- After a sometime without being used the API will lose the connection to the game server so when you open the GUI the first time you might see an error that it can't fetch the list of players. However this will recover on its own just refresh or wait til the next auto refresh

- The game server in rare case fails to return the steam ID of a player. 

- We logs are completely empty the game server will fail to respond to the request causing an error to show in the API/GUI

- The RCON api server truncates the name of players to a maximum of 20 charcheters even though, up to 32 characters are displayed in game. Bottom line you don't always see the full name



## How to use

Demo video coming soon

## Features to come 

More or less in order of priorities

- Individual moderators accounts
- Audit trail
- Players sessions history (with records of actions applied to players)
- Deferred bans (from a blacklist)
- Custom preset punish/kick/ban messages
- Performance improvements for the player list view
- Auto randomisation of map rotation (scheduling of the endpoint: /api/do_randomize_map_rotation)
- Integration with Nitrado
- Full log history (stored permanently)
- Action hooks on chart messages and players connect / disconnect
- Integration with Discord 

## USAGE of the CLI with docker

##### Build the image
    $ docker build . -t rcon

##### Set your server info as environement variables and run the cli
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
