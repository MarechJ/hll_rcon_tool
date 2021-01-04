# Hell Let Loose (HLL) advanced RCON  

An extended RCON tool for Hell Let loose.
It's composed of HTTP Api, a friendly GUI and if you need it a cli or use it as a library to build your own client.

Please join us on discord if you use it, for feedback, troubleshooting and informations about updates: https://discord.gg/hZx6gn3

Feel free to contribute, some parts would need a rewrite (I single-handedly built it so I took some shortcuts).
There's a LOT of new cool features that could be added, I'd be happy to walk through the code with you if you want to get involved.

Here's a sample:
![Live view page](/images/Rcon.png)
![Settings](/images/Rcon2.png)
![Player history overview](/images/Rcon3.png)
![Historical logs](/images/Rcon4.png)

# How to install the App

### Pre-requistes:

  - Having some basic shell (command prompt) skills. Feel free to ask for help on the Discord
  - Having a dedicated server - This app is meant to run 24/7 (it's a website with attached services)
  - The below isntalled on the server where you install it:
     - (Otionnal but recommanded) GIT: https://git-scm.com/downloads
     - Docker Engine (Community) installed: https://docs.docker.com/install/
     - Docker Compose installed: https://docs.docker.com/compose/install/

## Install steps

### 1. Get the sources

    git clone https://github.com/MarechJ/hll_rcon_tool.git
    cd hll_rcon_tool

If you don't have git you can also download the [latest zip release](https://github.com/MarechJ/hll_rcon_tool/releases/latest), however it's much less practical for updating.

Note: If you have several servers, clone it multiple times in different directories like below (if you'd like your servers to share a DB for Blacklists contact us on discord)

    git clone https://github.com/MarechJ/hll_rcon_tool.git hll_rcon_tool_server_number_2
    cd hll_rcon_tool_server_number_2


__From here all the commands assume that you are at the root of the repo you just cloned__

### 2. Set your server informations. Edit the `.env` file and fill in the blanks (for all your servers) like so:

Note if you don't see the `.env` file you need to activate the show hidden files option on windows. On linux don't forget the `-a`: `ls -a`

    # Ip address of the game server
    HLL_HOST=22.33.44.55
    # Rcon port (not the query one!)
    HLL_PORT=20310
    # Your rcon password (the one you use with your current Rcon)
    HLL_PASSWORD=mypassword
    # Choose a password for your Database (you probably won't need it)
    HLL_DB_PASSWORD=mydatabasepassword

    # The two below are the username and password that will be required to access the ronc website. 
    # I recommand using a different password that the RCON one
    # If you want to change it later, just change it here then run the command to start the app
    RCONWEB_USERNAME=myteam
    RCONWEB_PASSWORD=mynewpassword
 
    # If you want all (important) actions to be sent to one of you discord channel, add the full webhook url below
    DISCORD_WEBHOOK_AUDIT_LOG=https://discordapp.com/api/webhooks/71...515/qRfJCT...Q5T

    # If you have multiple servers, also change these lines (each server must have a different port, just increment the number)
    RCONWEB_PORT=8011
    HLL_DB_HOST_PORT=5433
    HLL_REDIS_HOST_PORT=6380


Note for power users:

You could also just export the variables in your terminal before running the docker-compose commands
OR edit the `docker-compose.yml` and replace the `${variable}` directly in there, however you might have a conflic next time you update the sources.
Alternatively you can also specify them in the command line. [More details](https://docs.docker.com/compose/environment-variables/#set-environment-variables-with-docker-compose-run)

### 3. RUN it!

#### Linux

    docker-compose up -d 

#### Windows

    docker volume create redis_data
    docker volume create postgres_data
    docker-compose -f docker-compose.yml -f docker-compose.windows.yml up -d 

#### Raspberry-Pi or any ARM32v7

    docker-compose -f docker-compose.yml -f docker-compose.arm32v7.yml build
    docker-compose -f docker-compose.yml -f docker-compose.arm32v7.yml  up -d 


The web application will be available on `<your server ip>:$RCONWEB_PORT` (you can use http://localhost:8010 if you test from the machine where it's installed)

Note: If you are running it on Windows prior to 10 docker runs in a virtual machine, so you have to [find the IP](https://devilbox.readthedocs.io/en/latest/howto/docker-toolbox/find-docker-toolbox-ip-address.html) of that VM.


### 4. CHANGE YOUR ADMIN PASSWORD

Using you browser go to `<your server ip>:$RCONWEB_PORT/admin` (8010 is default port) and login with user: `admin` password: `admin`
FIRST THING YOU MUST DO IS CHANGE YOUR PASSWORD there: http://prntscr.com/u3t2ms
After that you can start adding youR users with this: http://prntscr.com/u3t2u4 
Make sure you specify their steam id it will be used in upcoming features: http://prntscr.com/u3t2yq
Once the user is created you'll end up on that page: http://prntscr.com/u3t3to
I recommend NOT CHANGING ANYTHING except for a select few of your most trusted staff members you can tick the `Superuser status`.
Please note that users won't be able to change their password by themselves unless you tick the `staff status` so that they can access this admin page, however i DO NOT RECOMMEND doing as I won't be maintaining special permissions on admin models on the future (just manage password for them). 
To change the password of one of your user, in the users list click on him, then there: http://prntscr.com/u3ytzi


Please note that the "onlineadmins" variable in the (auto) broadcast is broken due to accounts. It will be fixed and improved later.

You're done, ENJOY!

### To update to the latest version:

#### In case it says your local changes the `.env` would be overriden when you git pull:

You can do 

   git stash && git pull

Then either: `git stash apply` edit to remove the conflit then `git reset .env`
Or just fill the `.env` manually again.
Then run the docker-compose commands.
This won't happen for every updates.



#### Linux

    git pull
    docker-compose pull && docker-compose up -d


#### Windows

    git pull 
    docker-compose pull && docker-compose -f docker-compose.yml -f docker-compose.windows.yml up -d 

#### Raspberry-Pi or any ARM32v7

    git pull 
    docker-compose -f docker-compose.yml -f docker-compose.arm32v7.yml build
    docker-compose -f docker-compose.yml -f docker-compose.arm32v7.yml  up -d 

Or download the [latest zip release](https://github.com/MarechJ/hll_rcon_tool/releases/latest)

Note that it's important you get the sources every time, or at least the docker-compose files, as new dependancies might be introduced

### To downgrade (in case of issue) to a previous version:

Check the availabe versions numbers on docker hub (or github releases):
https://hub.docker.com/r/maresh/hll_rcon/tags
https://github.com/MarechJ/hll_rcon_tool/releases

Edit you docker-compose.yml and change all the images from:

    image: maresh/hll_rcon:latest
    ...
    image: maresh/hll_rcon_frontend:latest

To the version you want (here we use v1.9)

    image: maresh/hll_rcon:v1.9
    ...
    image: maresh/hll_rcon_frontend:v1.9


## Known issues and limitations

- After a sometime without being used the API will lose the connection to the game server so when you open the GUI the first time you might see an error that it can't fetch the list of players. However this will recover on its own just refresh or wait til the next auto refresh
- The game server in rare case fails to return the steam ID of a player. 
- When logs are completely empty the game server will fail to respond to the request causing an error to show in the API/GUI
- The RCON api server truncates the name of players to a maximum of 20 charcheters even though, up to 32 characters are displayed in game. Bottom line you don't always see the full name


## How to use

Demo video coming soon

There's a public endpoint available to anybody without password on http://<yourip>:<yourport>/api/scoreboard

See [User Guide](USERGUIDE.md) for more information on how to use certain features of the app. 

## Features to come 

More or less in order of priorities

- Individual moderators accounts
- Audit trail
- ~~Players sessions history (with records of actions applied to players)~~
- ~~Deferred bans (from a blacklist)~~
- Custom preset punish/kick/ban messages
- ~~Performance improvements for the player list view~~
- Auto randomisation of map rotation (scheduling of the endpoint: /api/do_randomize_map_rotation)
- Full log history (stored permanently)
- ~~Action hooks on chat messages and players connect / disconnect~~
- ~~Integration with Discord~~

## USAGE of the CLI with docker

### Build the image
    $ docker build . -t rcon

### Set your server info as environement variables and run the cli

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

    $ docker run -it -e HLL_HOST=1.1.1.1 -e HLL_PORT=20300 -e HLL_PASSWORD=mypassword rcon python -m rcon.cli get_maps

      [2020-05-03 17:15:00,508][DEBUG] rcon.commands commands.py:_request:90 | get mapsforrotation
    ['foy_warfare', 'stmariedumont_warfare', 'hurtgenforest_warfare', 'utahbeach_warfare', 'omahabeach_offensive_us', 'stmereeglise_warfare', 'stmereeglise_offensive_ger', 'foy_offensive_ger', 'purpleheartlane_warfare', 'purpleheartlane_offensive_us', 'hill400_warfare', 'hill400_offensive_US']


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

    docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d redis postgres

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

#### Run a server

    # from the root of the repo
    pip install -r requirements.txt
    PYTHONPATH=$PWD  DJANGO_DEBUG=true ./rconweb/manage.py runserver

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


#### To test your changes will work with the prod setup, start the whole stack 

    docker-compose -f docker-compose.yml -f docker-compose.dev.yml build
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

Now test on http://localhost:8010

#### General notes:

If you have problems with dependancies or versions of python or nodejs please refer to the respective Dockerfile that can act as a guide on how to setup a development environment.
If you need a refresher on which process needs what variables have a look at the docker-compose file.