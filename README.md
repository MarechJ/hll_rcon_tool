![Website](https://img.shields.io/website?down_color=red&up_color=orange&up_message=hllrcon.app&url=https%3A%2F%2Fhllrcon.app)
![Discord](https://img.shields.io/discord/685692524442026020?color=%237289da&label=discord)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/marechj/hll_rcon_tool)
![Docker Cloud Automated build](https://img.shields.io/docker/cloud/automated/maresh/hll_rcon)
![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/maresh/hll_rcon)
![Docker Pulls](https://img.shields.io/docker/pulls/maresh/hll_rcon)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/T6T83KY8H)

# Hell Let Loose (HLL) advanced RCON

An extended RCON tool for Hell Let loose, meant to replace and go WAY beyond the official tool.

It is essentially a website that you can self host (or if you ask around the discord, some people can probably host it for you)

## Included features:

- Live view on players + all expected actions: message, punish, kick, temporary ban (choose the time), permanent ban. Search for players, and sort by play time, punishments, name etc. etc.
- Live updating game view (can see players per team, squad, roles, levels, score, etc.) and perform actions on individuals, squads, the entire team or server.
- User account and audit logs, each moderator has it's own account so you know who did what on whom and when, all the rcon actions can get forwarded to your discord (change of settings included)
- Group actions - Easily apply the same action on multiple players with one click (say you want to switch or kick a whole squad)
- Live logs + filtering by type (kill, chat, vote, etc..), filtering by players
- Discord webhooks support, so that the chat, TK and kills can be forward to your discord server
- Trigger word that when written in the ingame chat will create an alert (tag a person(s) or a role(s) on discord) such as: !admin or just any word you want (insults if you want to chase those)
- Flag player with any emoji / icons you want + comment attached
- Auto loading of player's country from steam and displayed in live view
- History of players and player profile: All game sessions of players are recorded, all the names they used in the past, punishments they have received and by which admin, etc
- Apply actions on players even if they are not online anymore, from the player history you can flag, watch, perma ban, temp ban, lift all bans and add to VIP.
- Permanent logs, a search tool to look at the entire history of the game logs of your server, export logs as CSV
- Multi server support, you can host the rcon for multiple servers and they will share the same player database, you can apply temp and perma bans to all server with only one action, synch VIP, settings, broadcast messages etc...
- Automated broadcast loops
- Automated settings based on the player count of you server
- Shared text for punishments and various messages that you can preset so that you never have to type the reason for the kick anymore. It also remember new text you type if you want it (to autocomplete it the next time)
- Search through bans by name, reason or steam ID (for quick unbanning)
- Backup of your bans so that if you ever change your game server or add one the bans will be re-applied on the fly if the banned dude tries to join your new server
- Recording of you map history, you see which map were played and how long they lasted
- Ban (blacklist) people even if they have never set foot on your server yet
- Basic scoreboard showing you total kills / death / TK / death by TK for the last N minutes
- Backup and restore/import of VIPs
- All the basic settings, map rotation management, sliders for idle kick time, max ping etc..
- For power users and coders: You can add anything you want in the cron server or in the supervisor service so it's easy to code you own plugin (I myself have a votemap plugin and a bot that verifies players), an HTTP API to use all the features above and a CLI for a subset of those
- Put player on a watch list and be notified when they enter your server
- Live stats, per game or per session with a friendly public version, as well as historical games (bookmarkable)

> Why a website?

- It's running 24/7 so you have A LOT features that you couldn't get with a simple desktop app (recording and forwarding of logs, discord alerts, player profile etc..)
- It's more secure / convenient, a website is centralized, meaning that all actions have to go through it, you don't need to give the real RCON password to you moderators, all activity is recorded in one place, you can share configuration with other, etc...
- It does not require any installation on the client side, you just need a browser

> Yes but I don't know anything about console commands, coding and such?

It's a 2 steps installation (5 if you include the pre-requisites), many not so technical people managed so you probably can too.
The community grew quite big so if you still don't understand what to do after reading this just go and ask on discord :)

There's also a Wiki made by the community (Thanks [2.Fjg]bn.hall): https://github.com/MarechJ/hll_rcon_tool/wiki

**Join us on discord if you use it, for feedback, troubleshooting and informations about updates:** https://discord.gg/hZx6gn3

Here's a sample:
![Live view page](/images/Rcon.png)
![Settings](/images/Rcon2.png)
![Player history overview](/images/Rcon3.png)
![Historical logs](/images/Rcon4.png)

# How to install the App

### Pre-requisites:

- It's recommended that you use Linux, you _should_ be able to set it up anywhere that you can get Docker to run, but don't expect much or any support if you don't install on Linux
- Having some very basic shell (command prompt) skills. Feel free to ask for help on the Discord! (please consult Google, Stackoverflow, etc.)
- Having a dedicated server - This app is meant to run 24/7 - (If you don't have that, you can just run a cheap Virtual Private Server)
- The below need to be installed on the server where the rcon will run:
  - (Optional but recommanded) `git`: https://git-scm.com/downloads (if you don't use git you need to download the releases)
  - `Docker Engine` (Community) installed: https://docs.docker.com/engine/install/
    - You can also use Docker Desktop but you may have issues with nested virtualization depending on your computer/server/VPS
  - `Docker Compose` installed: https://docs.docker.com/compose/install/
    - You should be able to use either `docker-compose` or `docker compose` depending on what you have installed, just adjust the commands below accordingly, but `docker-compose` is deprecated now, this README and release announcements will show `docker compose` examples, if you haven't upgraded it is up to you to modify the commands and know what you are doing.

## Install steps

### 1. Get the sources

    git clone https://github.com/MarechJ/hll_rcon_tool.git
    cd hll_rcon_tool

If you don't have `git` you can also download the [latest zip release](https://github.com/MarechJ/hll_rcon_tool/releases/latest), however it's much less practical for updating.

### Multiple Game Servers

You can use one CRCON for multiple game servers, or have separate CRCONs for one (or more) game server, but they need to be set up differently, see below.

For instance if you run multiple game servers (for instance US west, US east and/or an event server) it makes more sense to do _one_ CRCON install rather than separate CRCONs for each game server.

#### One CRCON Multiple Game Servers

When using a single CRCON installation for multiple game servers all of your admin accounts will have equal access to all of them, and all of your data will be stored in a single database.

This will make it difficult to separate your servers in the future (for instance if you are trying to use one CRCON for multiple communities by sharing a VPS) without starting from scratch and losing data.

**Note**: Setting up more than **3** game servers in a single installation will require you to edit your `.env` and `docker-compose.yml` and add new sections for each server past the third.

#### Multiple CRCON Installations

If you do not want to mix admin accounts and database data you can clone it multiple times in different directories (see below) and then set each of them up (and then set up as many game servers per CRCON that you choose). This makes more sense when you're sharing the server you host CRCON on with other communities.

**Note**: When you run two or more CRCONs on the same machine you will have redis/postgres port conflicts and will need to resolve these in your `.env` and compose files.

    git clone https://github.com/MarechJ/hll_rcon_tool.git hll_rcon_tool_server_number_2
    cd hll_rcon_tool_server_number_2

**From here all the commands assume that you are at the root of the git repository you just cloned!**

### 2. Set your server informations. Edit the `.env` file and fill in the blanks (for all your servers) like so:

Make a copy of `default.env` and name it `.env` (it must be named exactly `.env`, this is how Docker identifies it)

```
cp default.env .env
```

**Note**: if you don't see the `.env` file you need to activate the show hidden files option on Windows. On Linux don't forget the `-a`: `ls -a`

**Note**: If you make _any_ changes to your `.env` you will have to recreate (`docker compose up -d --force-recreate --remove-orphans` your containers before it will take effect), (if you `docker compose restart` it will not take effect)

**Note**: The values in `.env` are used by `docker` when it starts the container and they're referenced in your `compose` files, you should only edit (unless you really know what you are doing) values in `.env` and not the `compose` files.

The comments in `.env` should be self explanatory, but these are the minimum you need to set the following environment variables. Do not add/delete/comment out/etc. fields unless you know what you are doing.

Global settings (affects all the servers inside of your CRCON installation)

    HLL_DB_PASSWORD
    RCONWEB_API_SECRET

Per server settings

    HLL_HOST
    HLL_PORT
    HLL_PASSWORD

**You must configure `RCONWEB_SERVER_URL` for each server you're setting up to match the URL you're hosting CRCON on, or you will be unable to access the admin site due to CSRF errors**

Because of how Django handles CSRF protection, you won't be able to use the admin site until you've configured your server URL. This used to be set in the environment as `RCONWEB_SERVER_URL` but is now set through the GUI (or command line) as the `server_url` value in your CRCON settings (`Settings > CRCON Settings` in the GUI drop down menu) or the value of `RconServerSettingsUserConfig` if you set it via the CLI.

This must be set to whatever URL you're accessing CRCON from (look at your browser window), such as `http://localhost:8010`, or whatever **your** domain is.

For example if you are hosting using `HTTPS` on `example.com` you would set it to `https://example.com`
For example if you are hosting using `HTTP` on `127.0.0.1` on port `8010` you would set it to `http://127.0.0.1:8010`

Note: when you're configuring multiple game servers inside one CRCON installation you need to make sure your `RCONWEB_PORT`s are unique and also not otherwise used on the machine your're hosting on, the defaults _should_ work.

### 3. Additional configuration

Many things are configurable, most of it is done through the GUI (or command line) to settings that are saved in the database. `config/supervisord.conf` controls how the services are started/restarted, etc.

**Note** for power users:

You can set the environment variables anyway that Docker accepts (setting them in the shell, specifying them on the command line, etc.) but it is much easier to just use the `.env` file and manage it that way. You can also manually edit the compose files, but it may cause you issues when upgrading and isn't recommended unless you know what you're doing.

[More details](https://docs.docker.com/compose/environment-variables/#set-environment-variables-with-docker-compose-run)

### 4. RUN it!

#### Linux

    docker compose up -d

#### Windows

    docker volume create redis_data
    docker volume create postgres_data
    docker compose -f docker-compose.yml -f docker-compose.windows.yml up -d

#### Raspberry-Pi or any ARM32v7

    docker compose -f docker-compose.yml -f docker-compose.arm32v7.yml up -d --build

The web application will be available on `<your server ip>:$RCONWEB_PORT` (you can use http://localhost:8010 if you test from the machine where it's installed)

**Note**: If you are running it on Windows prior to 10 Docker runs in a virtual machine, so you have to [find the IP](https://devilbox.readthedocs.io/en/latest/howto/docker-toolbox/find-docker-toolbox-ip-address.html) of that VM.

### 5. CHANGE YOUR ADMIN PASSWORD

Using your browser go to `<your server ip>:$RCONWEB_PORT/admin` (8010 is the default port) and login with user: `admin` password: `admin`
FIRST THING YOU MUST DO IS CHANGE YOUR PASSWORD (see the red box in the top right): ![](images/readme_admin_password_1.png)  
After that you can start adding your users with this: ![](images/readme_admin_account_setup_1.png)  
Make sure you specify their steam ID it will be used in upcoming features: ![](images/readme_admin_account_setup_2.png)  
Once the user is created you'll end up on that page: ![](images/readme_admin_account_setup_3.png)  
I recommend NOT CHANGING ANYTHING except for a select few of your most trusted staff members you can tick the `Superuser status`.
Please note that users won't be able to change their password by themselves unless you tick the `staff status` so that they can access this admin page, however i DO NOT RECOMMEND doing as I won't be maintaining special permissions on admin models on the future (just manage password for them).
To change the password of one of your user, in the users list click on him, then there: ![](images/readme_admin_account_setup_4.png)

Please note that the `onlineadmins` variable in the (auto) broadcast is broken due to accounts. It will be fixed and improved later.

You're done, ENJOY!

If you feel generous you can donate, the money will be use to reward contributing developer or content creator to create video tutorial, demos, documentation, etc.
[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate?hosted_button_id=56MYGQ2966V7J)

### To update to the latest version:

Please join the discord and follow announcements, sometimes the update instructions vary from standard. If you are updating from an older version you should review the announcements in order and make any non-standard changes in order.

### Normal (most) updates

#### Linux

Pull the changes from github:

    git fetch --tags

Check out a tagged release (substitute the release you want):

    git checkout v7.0.2

Get the newest docker images and restart your containers:

    docker compose pull
    docker compose up -d --force-recreate --remove-orphans

#### Windows
Substitute the release you want in `git checkout`:

    git fetch --tags
    git checkout v7.0.2
    docker compose pull && docker compose -f docker-compose.yml -f docker-compose.windows.yml up -d --force-recreate --remove-orphans

#### Raspberry-Pi or any ARM32v7
Substitute the release you want in `git checkout`:

    git fetch --tags
    git checkout v7.0.2
    docker compose -f docker-compose.yml -f docker-compose.arm32v7.yml up --build -d --force-recreate --remove-orphans

Or download the [latest zip release](https://github.com/MarechJ/hll_rcon_tool/releases/latest)

**Note**: If you get any sort of `git` error messages when you pull you have to resolve these before you can upgrade. Unless you have been changing files this should never happen.

**Note**: that it's important you get the sources every time, or at least the docker-compose files, as new dependancies might be introduced

### To downgrade (in case of issue) to a previous version:

Check the available versions numbers on docker hub (or github releases):
https://hub.docker.com/r/maresh/hll_rcon/tags
https://github.com/MarechJ/hll_rcon_tool/releases

Edit your `.env` file and change `TAGGED_VERSION` from `latest` to a specific tagged release you want the images for (it **must** match the release tag on Docker hub):

    TAGGED_VERSION=9.1.1

Reverse any changes you made (from the previous upgrades, if any) you had to do as part of the upgrade process, consult the release notes or the announcement on the Discord.

### Note for multi servers beyond 3 servers

You can copy the the last server section in the docker-compose.yml file and paste it, while replacing all the \_3 by \_4, also add the required variable in your .env (copy a whole section and replace the \_3 to \_4 suffix)
Also note that you must add this extra keys in your docker-compose.yml after HLL_REDIS_URL. And mind the DB number that should change with each server

```
      ....
      HLL_REDIS_URL: redis://redis:6379/1
      HLL_REDIS_HOST: redis
      HLL_REDIS_PORT: 6379
      HLL_REDIS_DB: 1
      ....
```

## How to use

Demo video coming soon

There's a public endpoint available to anybody without password on http://<yourip>:<yourport>/api/scoreboard

See [User Guide](USERGUIDE.md) for more information on how to use certain features of the app.

## Features to come

More or less in order of priorities

- ~~Individual moderators accounts~~
- ~~Audit trail~~
- ~~Players sessions history (with records of actions applied to players)~~
- ~~Deferred bans (from a blacklist)~~
- ~~Custom preset punish/kick/ban messages~~
- ~~Performance improvements for the player list view~~
- ~~Auto randomisation of map rotation (scheduling of the endpoint: /api/do_randomize_map_rotation)~~
- ~~Full log history (stored permanently)~~
- ~~Action hooks on chat messages and players connect / disconnect~~
- ~~Integration with Discord~~
- Leaderboard and all time stats

## Building your own Docker images

Docker images are hosted on [Docker Hub](https://hub.docker.com/r/maresh/hll_rcon), but if you're running a fork, have made local modifications or the release you want isn't available for some reason, you can build your images locally.

## Set environment variables

If you don't already have a `.env` file created use `default.env` to make a template and you'll be able to build the images without setting the :

    cp default.env .env

If you don't have a `.env` you wou must set the following environment variables to something, or the build will fail with an error that looks like `invalid tag ":": invalid reference format` (just use a copy of `default.env`):

    BACKEND_DOCKER_REPOSITORY=
    FRONTEND_DOCKER_REPOSITORY=
    TAGGED_VERSION=

### Build the images

    docker compose -f docker-compose.yml -f docker-compose.dev.yml build 

### Run it!

Once the images are built (which can take a considerable amount of time depending on your hardware specs), and once it's configured properly (see the installation part of this README), then simply use `docker compose` to create the containers:

    docker compose up -d --force-recreate --remove-orphans

If you don't want to use `docker compose` (which you really should, it's just easier) then you would have to properly set/create/run the Docker containers yourself, consult Docker's documentation please.

## Development Environment

Pull requests are always welcome! It can be a bit tricky setting up a local environment and it is hard to contribute without having a HLL game server to connect to (and it's impossible to host one yourself, they won't release the server files).

### Overview / Project Structure

The project is split up into several main components (the `backend`, `frontend`, services run by `supervisord` and `redis` and `postgres` that is shared across each image), and is intended to be run using Docker and `docker compose`. Each CRCON install can manage multiple game servers, and each game server (server 1, server 2, etc.) has its own set of images (backend_1, frontend_1, supervisor_1, etc.)

The `backend` is split into two major components, the `rcon` package and the `rconweb` package which is a `Django` web (`WSGI`) application.

`rcon` handles the implementation of the [HLL RCON protocol](https://gist.github.com/timraay/5634d85eab552b5dfafb9fd61273dc52) and implements most of the core behavior/features that CRCON has.

`rconweb` handles all of the web portions (URL routing, authentication, sessions, etc.) once a HTTP request has been received by `nginx` in the `frontend`.

The `supervisor` container manages starting and restarting all of the optional/non optional (if you want a fully functioning CRCON) services, all of which are implemented in the `rcon` package or are a standalone program like `rq` or `cron`.

The `frontend` is a combination of `nginx` (used as a reverse proxy) and `gunicorn` web servers that handles all of the HTTP requests and serves all of the responses. The flow is `incoming request` -> `nginx` -> `gunicorn` -> `nginx` -> `outgoing response`. `nginx` handles serving all of the static content like HTML/css/images, and `Django` processes all of the API calls that return dynamic content. 

#### `rcon` package

The `rcon` package relies on several core classes.

`rcon.connection.HLLConnection` handles connecting to the game server (IP, port and RCON password), `xor` [encoding/decoding](https://gist.github.com/timraay/5634d85eab552b5dfafb9fd61273dc52#protocol-1) content and sending/receiving raw bytes over TCP sockets.

`rcon.commands.ServerCtl` is the parent class of `Rcon` and handles managing a pool of `HllConnection` instances, validating/converting low level stuff (like stripping tabs from user generated content for HLL tab delimited lists), automatically retrying commands that fail, and sending the raw commands (such as `get profanity`) to the game server.

`rcon.commands.ServerCtl` can be used without any database or redis connection, but is of limited use and not published separately.

`rcon.rcon.Rcon` inherits from `ServerCtl` and handles parsing/structuring the raw text received from the game server into meaningful data, interacting with the database, caching command results, etc.

`CRCON` is not an async (`ASGI`) web app (`async`) or multi core (`multiprocessing`), but it does support running multiple slow (to the game server) requests simultaneously through [thread pools](https://docs.python.org/3/library/concurrent.futures.html).

The `rcon` package also contains the implementation of most of CRCNs features, if you're not sure how something works, identify which API endpoint is doing the action, look in the URL routing in `rconweb` and you can see what parts of `rcon` are imported.

#### `rconweb`

The `rconweb` package is a Django web app that actually exposes all of the URL endpoints and imports from `rcon` as needed when interacting with the game server versus the local CRCON backend (`redis`, `postgres`, etc.).

Some endpoints are explicitly exposed, but some (`Rcon` methods) are implicitly exposed (`rconweb.api.views.expose_api_endpoint`).

#### `supervisord`

Due to the fact that Python is notoriously [single threaded](https://stackoverflow.com/questions/1294382/what-is-the-global-interpreter-lock-gil-in-cpython), some core parts of CRCON have been broken out into services that run in their own Python interpreter so they can take advantage of multiple cores/threads on the system. This also enables faster network access since each individual network request (to the game server, steam API, discord, etc.) blocks until completion.

Other portions are optional services and have been split so users have more control over what runs.

The services are managed by [supervisord](http://supervisord.org/) and run inside of their own (`supervisor`) container.

#### `redis`

[Redis](https://redis.io/) is used for two reasons in CRCON, caching and interprocess communication.

Every round trip to the game server can be significantly slow (in computing terms) and induces some amount of overhead on both CRCON and the game server. 

Some commands are cached even if they have a very low cache time (such as retrieving logs from the game server) to avoid constantly reprocessing info on very short time frames and others are on a longer cache time because they rarely if ever change (such as the list of available maps from the game server).

This also condenses requests that occur almost simultaneously to be reduced to a single request that makes it to the game server, the remaining requests will be resolved from the cache (unless they happened before the first request has completed and cached its results).

Many portions of CRCON run in their own separate Python interpreter instances with their own section of memory, but by caching results with redis, we can communicate back and forth between interpreter instances. This is used both explicitly with `rq` to run tasks (such as recording game stats to the database, or bulk VIP uploads) and implicitly when something caches function results in redis and is accessed elsewhere.

#### `postgres`

CRCON uses postgres 12 with a default configuration.

### Running a local/development instance

To run a local instance of CRCON without using the Docker images requires you to do some manual set up.

If you have **never** successfully run the complete CRCON environment from this install, you should do so first so that the database is created/initialized properly. (If you only ever plan on running the tests, you can do this without seeding the database).  If you've done this, you can skip the database migrations/user creation below. It's just easier to do it this way, so I recommend it but it is optional.

Because of some configuration differences and how Docker determines environment variable precedence, I recommend using separate shells to run local instances and to run the full blown production Docker setup.

To avoid polluting your system Python, you should create/activate a [virtual environment](https://realpython.com/python-virtual-environments-a-primer/), I use [pyenv](https://github.com/pyenv/pyenv) but set up is outside the scope of this README.

Once the virtual environment is activated in your shell install all of the Python dependencies:

    pip install -r requirements.txt
    pip install -r requirements-dev.txt  

#### Set environment variables

You can use `dev.env` as a template for what variables need to be set, and after filling in the missing portions, from your shell:

Or you can manually set them as specified in the sections below.

    source dev.env

`SERVER_NUMBER` is an integral part of how CRCON works and is how data is segregated between servers in the database and is normally set in the compose files.

    export SERVER_NUMBER=1

The `HLL_DB_PASSWORD` password must match what you set when the database was first created, or you can connect to the postgres docker container and [reset the password](https://stackoverflow.com/questions/12720967/how-can-i-change-a-postgresql-user-password) for your database user if needed.

The default username and database name is `rcon` if you've seeded the database unless you've configured it differently.

    export HLL_DB_PASSWORD=rcon_dev
    export HLL_DB_NAME=rcon
    export HLL_DB_USER=rcon
    export HLL_DB_HOST=localhost
    export HLL_DB_HOST_PORT=5432
    export HLL_DB_URL=postgresql://${HLL_DB_USER}:${HLL_DB_PASSWORD}@${HLL_DB_HOST}:${HLL_DB_HOST_PORT}/${HLL_DB_NAME}

#### Running the development backend

Make sure you set all of the environment variables from the previous section(s).

You can *sort of* run a local instance without a game server to connect to, but so much depends on one that it's pretty pointless to try to do this without one.

    export HLL_HOST=<your game server IP>
    export HLL_PORT=<your game server RCON port>
    export HLL_PASSWORD=<your game server RCON password>

**If you didn't run the production environment first**: Create the database tables (you only need to do this once, unless you've created new migrations).

    PYTHONPATH=. alembic upgrade head
    PYTHONPATH=. ./manage.py init_db
    PYTHONPATH=. ./rconweb/manage.py makemigrations --no-input 
    PYTHONPATH=. ./rconweb/manage.py migrate --noinput

Alembic runs the database migrations which creates the tables, and `init_db` installs a postgres extension and sets default values for auto settings.

`makemigrations` and `migrate` creates the required Django database tables.

**If you didn't run the production environment first**: Create a `superuser` account and follow the prompts:

    PYTHONPATH=. ./rconweb/manage.py createsuperuser       

Set the redis environment variables:

    export HLL_REDIS_HOST=localhost
    export HLL_REDIS_HOST_PORT=6379
    export HLL_REDIS_DB=1
    export HLL_REDIS_URL=redis://${HLL_REDIS_HOST}:${HLL_REDIS_HOST_PORT}/1

Both the `redis` and `postgres` containers should be running (or you should have a `redis` and `postgres` installed/configured if you don't want to use the Docker images):

    docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --force-recreate redis postgres

Start the Django (backend) development web server:

    DJANGO_DEBUG=true DEBUG=true PYTHONPATH=. ./rconweb/manage.py runserver --nothreading

If you've set all the environment variables correctly, initialized the database and started the Django web server, you'll see something similar to:

    System check identified some issues:

    WARNINGS:
    api.DjangoAPIKey: (models.W042) Auto-created primary key used when not defining a primary key type, by default 'django.db.models.AutoField'.
            HINT: Configure the DEFAULT_AUTO_FIELD setting or the ApiConfig.default_auto_field attribute to point to a subclass of AutoField, e.g. 'django.db.models.BigAutoField'.
    api.SteamPlayer: (models.W042) Auto-created primary key used when not defining a primary key type, by default 'django.db.models.AutoField'.
            HINT: Configure the DEFAULT_AUTO_FIELD setting or the ApiConfig.default_auto_field attribute to point to a subclass of AutoField, e.g. 'django.db.models.BigAutoField'.

    System check identified 2 issues (0 silenced).
    December 28, 2023 - 22:35:19
    Django version 4.2.7, using settings 'rconweb.settings'
    Starting development server at http://127.0.0.1:8000/
    Quit the server with CONTROL-C.

You can now open your browser (or use any other tool like [Postman](https://www.postman.com/)) to make API calls (http://127.0.0.1:8000/api/ will list all the available endpoints), or use the admin site (http://127.0.0.1:8000/admin/).

Any changes to the files in `rcon/` or `rconweb/` will cause the backend webserver to reload with the changes.

#### Running the development frontend

Once you have the development backend running, from another shell you can run the development frontend web server:

    cd rcongui
    npm install
    npm start

You should see something similar to:

    VITE v4.3.9  ready in 320 ms

    ➜  Local:   http://localhost:3000/
    ➜  Network: use --host to expose
    ➜  press h to show help

You can now open your browser (http://localhost:3000/) to use the frontend, any modifications to the frontend (javascript files) in `rcongui` will cause it to recompile/update.

#### Running services

Running the Django development web server **only** starts the backend web server which accepts HTTP requests, it won't start any of the services that would be started in a production environment.

Some of these services are required if you want the frontend to work as expected, such as `log_loop` (runs all of the hooks) or `log_recorder` that saves log lines to the database.

Each service you want to run either needs to be run in the background or needs to be run in a separate shell (don't forget to set environment variables in each shell)

    # Calculates player stats for the scoreboard
    PYTHONPATH=. ./manage.py live_stats_loop
    # Runs hooks (on connected events, on kills, etc.)
    PYTHONPATH=. ./manage.py log_loop
    # If you want logs to be saved in the DB
    PYTHONPATH=. ./manage.py log_recorder

Those service are run by supervisor in the production setup, so if you want more info check `config/supervisor.conf`

#### Running Tests

Unfortunately at this moment in time the database needs to be running for the tests to run. The tables don't actually need to exist.

From the root `hll_rcon_tool` directory:

    PYTHONPATH=. DEBUG=TRUE pytest tests/    

If you don't set `PYTHONPATH` you'll see errors similar to ` ModuleNotFoundError: No module named 'rcon'`.

If you don't set `DEBUG` to a truthy value, you'll see errors about not being able to connect to redis.


#### To test if your changes will work with the production setup, start the whole stack

This should be done from a **separate** shell without the environment variables set, or they'll override what is set in your `.env` file because of how Docker determines precedence and you won't be able to connect to `redis` or `postgres` properly.

Building the frontend if you've made any changes to the javascript files or if the build cache isn't available can take a considerable amount of time.

    docker compose -f docker-compose.yml -f docker-compose.dev.yml build
    docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --force-recreate

Now test on http://localhost:8010

#### General notes:

If you have problems with dependancies or versions of python or nodejs please refer to the respective Dockerfile that can act as a guide on how to setup a development environment.

If you need a refresher on which process needs what variables have a look at the docker-compose.yml file.
