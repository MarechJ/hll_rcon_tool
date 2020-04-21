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

    git pull && docker-compose pull && docker-compose up -d

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


## Development environment

First a quick overview of how the software is structured:

![Components overview](/images/overview.png)

The backbone of the application is HLLConnection + ServerCtl it is what binds the HLL Server rcon commands to the application.
The `Rcon` and `RecordedRcon` provide some wrapping around the raw results of the game server. And expose some new commands that are a combination of basic commands.
The `Rcon` class also adds a caching layer using Redis (or falling back to in-memory) in order to go easy on the server. 
The `RecordedRcon` is an additional wrapping where all the commands that should be saved, or use the Database should go.
I made the choice of separating the `ServerCtl`, `Rcon` and `RecorededRcon` into serparated layers to leave the possiblity to choose the right level of abstraction for what you need.

The API in django is a very thin layer that basically loops over all the methods available in `RecorededRcon` (and therefore all those of `ServerCtl` and `Rcon`) and binds them to a route see [/rconweb/api/views.py](/rconweb/api/views.py).
This is a bit hackish, but it saved me a lot of time a the begining, it also removes a lot of boilerplate, but it should probably change at some point to provide a cleaner set of endpoints.

### Start a development instance

#### First boot up the dependancies. I use docker for that but you can also install Redis and Postgres natively if you prefer

    docker-compose -f docker-compose-dev.yml up -d redis postgres

This will make redis and postgres available on you localhost with their default ports. If you need different port bindings refer to the `docker-compose-dev.yml` file

#### Then run an API using Django's development server:

**Note**: remember that you need to define some environment variables:

    export HLL_PASSWORD=<fill in yours>
    export HLL_PORT=<fill in yours>
    export HLL_HOST=<fill in yours>
    export HLL_DB_PASSWORD=developmentpassword
    export DJANGO_DEBUG=True
 
    export DB_URL=postgres://rcon:developmentpassword@localhost:5432
    export REDIS_URL=redis://localhost:6379/0

Run a server

    # from the root of the repo
    pip install -r requirements.txt
    PYTHONPATH=$PWD ./rconweb/manage.py runserver

This will run a development server on http://127.0.0.1:8000/ it auto refreshes on code changes
If you change the port rember that you will also need to change it in rcongui/.env for the frontend to know where to talk to the API

Hitting http://127.0.0.1:8000/api/ with Django DEBUG set to true will show you all the available endpoints. They are basically named after the methods of the `Rcon` class
All endpoints accept GET querystring parameters OR (not both at the same time) a json payload. The parameters are the same as the parameter names of the `Rcon` methodds (all that is auto generated remember).
It is not best practice to have endpoints that do write operations accept a GET with query string parameters but it was just easier that way. 

#### Now start the frontend:

    # from the root of the repo
    cd rcongui/
    npm install
    npm start

The GUI should now be available on http://localhost:3000/ it auto refreshes on code changes

#### General notes:

If you have problems with dependancies or versions of python or nodejs please refer to the respective Dockerfile that can act as a guide on how to setup a development environment.
If you need a refresher on which process needs what variables have a look at the docker-compose file.