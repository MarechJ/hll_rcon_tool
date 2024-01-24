![Website](https://img.shields.io/website?down_color=red&up_color=orange&up_message=hllrcon.app&url=https%3A%2F%2Fhllrcon.app)
![Discord](https://img.shields.io/discord/685692524442026020?color=%237289da&label=discord)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/marechj/hll_rcon_tool)
![Docker Cloud Automated build](https://img.shields.io/docker/cloud/automated/maresh/hll_rcon)
![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/maresh/hll_rcon)
![Docker Pulls](https://img.shields.io/docker/pulls/maresh/hll_rcon)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/T6T83KY8H)

Join us on discord if you use it, for feedback, troubleshooting and informations about updates: https://discord.gg/hZx6gn3

# Hell Let Loose (HLL) advanced RCON

An extended RCON tool for Hell Let loose, meant to replace the official tool and go WAY beyond.  

## Included features

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

## Some images
![Live view page](/images/Rcon.png)
![Settings](/images/Rcon2.png)
![Player history overview](/images/Rcon3.png)
![Historical logs](/images/Rcon4.png)

## Features to come

- Leaderboard and all time stats

# Installation

## Install on a VPS, not on your home PC

CRCON is designed to operate as a website,  
offering A LOT of features that you couldn't get with a desktop app  
(recording and forwarding of logs, Discord alerts, player profile, etc).

A website is more secure / convenient to manage a game server because :
- you don't need to give the real RCON password to you moderators ;
- all actions have to go through it : all activity is recorded in one place ;
- It does not require any installation on the client side, you just need a browser.

Although it is possible to install CRCON on any computer which is able to run Docker,  
we recommend installing it on a remote VPS server.

If you decide to install it on a home computer, keep in mind you'll have to :
- run your computer 24/7  
*hope you like noisy fans, hardware maintenance and electricity bills* ;
- open your home internet access and let people connect to your computer.  
  *This requires network management knowledge and could lead to security risks.*

## Hardware requirements

- Minimum : 2 CPU cores and 6GB of RAM.
- Recommended : 4 CPU cores and 8GB of RAM.
- Regarding drive space, the CRCON database of a game server where 95+ players connect for 10 hours per day may grow up to 20 GB in a year.  
As it's not easy to shrink it, you are advised to select an offer with >50 GB of storage.

Some VPS providers rent this type of services for ~$10/month.

## Software requirements

We recommend that you install CRCON on Linux, most preferably on a Debian-based distro, like Ubuntu.  
You won't get as much support on forums/Discords if you're using Windows.

These programs need to be installed on the server :

- *(Optional but highly recommanded)* `git` : https://git-scm.com/downloads  
  (if you don't use git, you'll have to manually download and install the releases in .zip format,  
  and you won't be able to update your CRCON as easily as with git)
- `Docker Engine` (Community) : https://docs.docker.com/engine/install/  
  You can also use Docker Desktop, but you may have issues with nested virtualization, depending on your computer/server/VPS.
- `Docker Compose` : https://docs.docker.com/compose/install/  
Note : `docker-compose` is deprecated.  
This README and release announcements will show `docker compose` examples.  
You should be able to use either `docker-compose` or `docker compose`, just adjust the commands below accordingly.

Some VPS providers offer free installation of linux distributions in which Docker is already activated. Search/ask for it !

## Install steps

*"I don't know anything about console commands, coding and such ?"*
- Stay cool and follow the drill. It's a simple installation, many not-so-technical people managed to do it, so you probably can too :)
- ~~There's also a Wiki made by the community (Thanks [2.Fjg]bn.hall): https://github.com/MarechJ/hll_rcon_tool/wiki~~  
*(The Wiki is obsolete. We hope we'll find the time to update it soon)*
- If you still don't understand what to do after reading this, just ask on Discord.

Note : all the commands given below are meant to be entered in a Debian-like Linux terminal.

### 1. Download CRCON

Using an SSH client (*don't know which one to get ?* Try https://putty.org/),  
**log as root** into your distant Linux, using the SSH credentials given by your VPS provider.

Enter these commands in the terminal (*press [Enter] to validate*) :

- download the CRCON files :  
  > `git clone https://github.com/MarechJ/hll_rcon_tool.git`
- get in the newly created CRCON dedicated folder :  
  > `cd hll_rcon_tool`

### 2. Edit the environment config file

Now, you're going to create and edit an **.env** file, in which you'll tell CRCON how to connect to your HLL game server.  
Here we'll use **nano**, a simple text editor that runs in text mode.  
*You can use any other tool you're used to, either local or getting the file from a SFTP connection.*

- make a copy of the environnement config file template :  
  > `cp default.env .env`
- install the nano text editor :  
  > `apt-get update && apt-get install nano`
- launch nano to edit the .env file :  
  > `nano .env`

In nano, you can move the cursor with the arrow keys.  
You do not have to change all the values. Only these 5 are mandatory :

1. Choose a password to give CRCON access to the database  
  (No need to remember/note it : you'll never have to enter it anywhere) :  

       HLL_DB_PASSWORD=anythingwithoutanyspace

2. Enter a long string that will be used to scramble users passwords  
  (No need to remember/note it : you'll never have to enter it anywhere) :

       RCONWEB_API_SECRET=anythingwithoutanyspaceordollarsign

In **SERVER 1** part :

3. Enter your RCON IP, as provided by the game server provider :

       HLL_HOST=123.123.123.123

4. Enter your RCON port, as provided by the game server provider :

       HLL_PORT=12345

5. Enter your RCON password, as provided by the game server provider :

       HLL_PASSWORD=yourrconpassword

Triple-check there is **no space before/after the `=` signs, nor in the values you've set**.
- save the changes with **Ctrl+o** (then type 'y' to validate)  
- exit nano with **Ctrl+x**


### 3. Run CRCON for the first time !

CRCON is now configured to start and connect to your HLL game server.  
But do not think it's over yet, as we now have to configure its users.

Note : Launch process will display a *lot* of scrolling text.  
Don't panic, as you do not have to read/do anything. Just watch the magic.

Enter the command(s) that suit(s) your operating system :

- Linux :
  > `docker compose up -d --remove-orphans`
- Windows :
  > `docker volume create redis_data`  
  `docker volume create postgres_data`  
  `docker compose -f docker-compose.yml -f docker-compose.windows.yml up -d`
- Raspberry-Pi or any ARM32v7 :
  > `docker compose -f docker-compose.yml -f docker-compose.arm32v7.yml up -d --build`

If eveything went well, you'll end up with some green lines saying "started" after a minute or two.  
CRCON has started !

If some of the final lines show (red) errors :  
recheck the values you've entered in the **.env** file and retry the starting process.

You may encounter a Docker error (*"bla bla **must be unique** bla bla"*) if you're using v2.24.1 of the docker-compose-plugin.  
This version has a bug that prevents Docker containers to start.  
If you encounter this error, you have to downgrade the docker-compose-plugin package version.  
- On Ubuntu 20.04 :
  > apt-get install docker-compose-plugin=2.21.0-1~ubuntu.20.04~focal
- On Ubuntu 22.04 :
  > apt-get install docker-compose-plugin=2.21.0-1~ubuntu.22.04~jammy

Then enter the start command line(s) above again.

### 4. Get in the CRCON UI

Your CRCON user interface can be reached from all over the world,  
in any web browser, using your VPS IP on port 8010 : http://yourVPSIP:8010/

- Get in there an click on **LOGIN**, in the top menu.  
The default credentials are `admin`/`admin`

*Don't touch anything yet. You'll have plenty of time to play with the different tools later.*

Now, we MUST change the admin password, as it is highly insecure !

### 5. Prepare to configure users

Due to inner security checks, we need to declare the VPS IP/port as "secure" to be able to enter the users management tool.

- In the **SETTINGS** menu, click on **CRCON settings** submenu  
  or directly get to http://yourVPSIP:8010/#/settings/rcon-server

  You'll see a large editable textarea.  
  The strange code in it is a config text, formatted in JSON.  
  Stay cool : for the time being, we only are going to change a single line in it.

- Modify the **server_url** line, entering your VPS IP and port 8010.  
You must have quotation marks `"` around the url, and a comma `,` as the final character on the line.

      "server_url": "http://yourVPSIP:8010/",

- Click on the **SAVE** link, below the textarea  
*(a green confirmation flag should pop in top-right corner of the window)  
If a yellow or red flag pops in, you have a syntax error : watch the example above to get it right)*

### 6. Restart CRCON

Yes. Restart it. This may sound strange, but it is mandatory :  
to be taken in account, the **server_url** value you've just set has to be declared during the CRCON Docker containers start.

Enter the command(s) that suit(s) your operating system :

- Linux :
  > `docker compose up -d --remove-orphans`
- Windows :
  > `docker compose -f docker-compose.yml -f docker-compose.windows.yml up -d`
- Raspberry-Pi or any ARM32v7 :
  > `docker compose -f docker-compose.yml -f docker-compose.arm32v7.yml up -d --build`

### 7. Configure users

Now you can get into the CRCON users management tool, located at : http://yourVPSIP:8010/admin

You should be already logged in. If not, the credentials are still `admin`/`admin`.

#### Add a new user

- Click on the **+Add** link.
![](images/readme_admin_account_setup_1.png)
- Fill the **Add User** form  
Don't forget to enter the user's Steam ID (see image below) : it will be used by CRCON to identify this user as an admin.
![](images/readme_admin_account_setup_2.png)
- Click on the **SAVE** link

Once the user is created, you'll end up on that page: ![](images/readme_admin_account_setup_3.png)

Please note that users won't be allowed to change their password by themselves unless you check `staff status`.

You can check the `Superuser status` to give all the permissions to your most trusted staff members.

To change the password of a user, click on its name, then on this link (see image below):  
![](images/readme_admin_account_setup_4.png)

You also can change *your* current password using the dedicated link (top-right red square below) :  
![](images/readme_admin_password_1.png)

#### Change default admin's password

- click on the page title **"Django administration"** to get back to the entry screen.  
*(This is the same as going to http://yourVPSIP:8010/admin)*
- click on **Users**, then on **admin**.
- You can change the default admin password (or uncheck the "Active" status to disable admin's account)
- Click on the **SAVE** button

### 8. Basic configuration is over !

Yes ! You did it ! You now have a fully working and secured CRCON ! Congratulations !

Take the time to explore all the menus and commands.

We *know* the UI isn't always intuitive and we would be glad if someone decide to help refreshing it ;)

You'll find a lot of things to customize in the "SETTINGS" menus.  
(Most of the settings are described/explained on their own page).

If you have any question, do not hesitate to ask it on the CRCON Discord.

Have fun !

---

If you feel generous you can donate,  
the money will be use to reward contributing developers or content creators  
to create video tutorial, demos, documentation, etc.  
[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate?hosted_button_id=56MYGQ2966V7J)

---

# Update to the latest version

Please join the CRCON Discord and follow announcements.  
Sometimes, update instructions vary from standard.  
If you are updating from an older version, you should review the announcements in order and make any non-standard changes in order.

### Normal (most) updates

#### Linux

- Pull the changes from github
  > `git fetch --tags`
- Check out a tagged release
  > `git checkout v9.4.1`
- Get the newest Docker images and restart your containers
  > `docker compose pull && docker compose up -d --remove-orphans`

#### Windows

- Pull the changes from github
  > `git fetch --tags`
- Check out a tagged release
  > `git checkout v9.4.1`
- Get the newest Docker images and restart your containers
  > `docker compose pull && docker compose -f docker-compose.yml -f docker-compose.windows.yml up -d --remove-orphans`

#### Raspberry-Pi or any ARM32v7

- Pull the changes from github
  > `git fetch --tags`
- Check out a tagged release
  > `git checkout v9.4.1`
- Get the newest Docker images and restart your containers
  > `docker compose -f docker-compose.yml -f docker-compose.arm32v7.yml up --build -d --remove-orphans`

You also can download the [latest zip release](https://github.com/MarechJ/hll_rcon_tool/releases/latest) and install it manually (not recommended)

**Note**: If you get `git` error messages when you pull, you have to resolve these before you can upgrade.  
Unless you have been changing files, this should never happen.  
**Note**: It's important you get the sources every time, or at least the docker-compose files, as new dependancies might have been introduced

# Downgrade (in case of issue) to a previous version

Check the available versions numbers on Docker hub (or Github releases) :  
https://hub.docker.com/r/maresh/hll_rcon/tags  
https://github.com/MarechJ/hll_rcon_tool/releases

Edit your `.env` file and change `TAGGED_VERSION` from `latest` to a specific tagged release  
(it **must** match the release tag on Docker hub):

    TAGGED_VERSION=9.4.1

# How to use

*Demo video coming soon*

There's a public endpoint available to anybody without password on http://yourVPSIP:7010/api/scoreboard

See [User Guide](USERGUIDE.md) for more information on how to use certain features of the app.

# For power users

## Multiple Game Servers

You can use one CRCON for multiple game servers, or have separate CRCONs for one (or more) game server, but they need to be set up differently, see below.
For instance if you run multiple game servers (for instance US west, US east and/or an event server) it makes more sense to do _one_ CRCON install rather than separate CRCONs for each game server.

#### One CRCON to manage multiple game servers

When using a single CRCON installation for multiple game servers all of your admin accounts will have equal access to all of them, and all of your data will be stored in a single database.
This will make it difficult to separate your servers in the future (for instance if you are trying to use one CRCON for multiple communities by sharing a VPS) without starting from scratch and losing data.
**Note**: Setting up more than **3** game servers in a single installation will require you to edit your `.env` and `docker-compose.yml` and add new sections for each server past the third.

#### Manage more than 3 servers

You can copy the the last server section in the docker-compose.yml file and paste it, while replacing all the \_3 by \_4, also add the required variable in your .env (copy a whole section and replace the \_3 to \_4 suffix)
Also note that you must add this extra keys in your `docker-compose.yml` after HLL_REDIS_URL. And mind the DB number that should change with each server

```
      ....
      HLL_REDIS_URL: redis://redis:6379/1
      HLL_REDIS_HOST: redis
      HLL_REDIS_PORT: 6379
      HLL_REDIS_DB: 1
      ....
```

#### Multiple CRCON installations

If you do not want to mix admin accounts and database data you can clone it multiple times in different directories (see below) and then set each of them up (and then set up as many game servers per CRCON that you choose).
This makes more sense when you're sharing the server you host CRCON on with other communities.
**Note**: When you run two or more CRCONs on the same machine, you will have redis/postgres port conflicts and will need to resolve these in your `.env` and compose files.

## Building your own Docker images

Docker images are hosted on [Docker Hub](https://hub.docker.com/r/maresh/hll_rcon), but if you're running a fork, have made local modifications or the release you want isn't available for some reason, you can build your images locally.

### Set environment variables

If you don't already have a `.env` file created use `default.env` to make a template and you'll be able to build the images without setting the :

> cp default.env .env

If you don't have a `.env` you wou must set the following environment variables to something, or the build will fail with an error that looks like `invalid tag ":": invalid reference format` (just use a copy of `default.env`):

    BACKEND_DOCKER_REPOSITORY=
    FRONTEND_DOCKER_REPOSITORY=
    TAGGED_VERSION=

### Build the images

> docker compose -f docker-compose.yml -f docker-compose.dev.yml build

### Run it !

Once the images are built (which can take a considerable amount of time depending on your hardware specs), and once it's configured properly (see the installation part of this README), then simply use `docker compose` to create the containers:

> docker compose up -d --remove-orphans

If you don't want to use `docker compose` (which you really should, it's just easier) then you would have to properly set/create/run the Docker containers yourself, consult Docker's documentation please.

## Development environment

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

If you have **never** successfully run the complete CRCON environment from this install, you should do so first so that the database is created/initialized properly. (If you only ever plan on running the tests, you can do this without seeding the database). If you've done this, you can skip the database migrations/user creation below. It's just easier to do it this way, so I recommend it but it is optional.

Because of some configuration differences and how Docker determines environment variable precedence, I recommend using separate shells to run local instances and to run the full blown production Docker setup.

To avoid polluting your system Python, you should create/activate a [virtual environment](https://realpython.com/python-virtual-environments-a-primer/), I use [pyenv](https://github.com/pyenv/pyenv) but set up is outside the scope of this README.

Once the virtual environment is activated in your shell install all of the Python dependencies:

> pip install -r requirements.txt

> pip install -r requirements-dev.txt

#### Set environment variables

You can use `dev.env` as a template for what variables need to be set, and after filling in the missing portions, from your shell:

Or you can manually set them as specified in the sections below.

> source dev.env

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

You can _sort of_ run a local instance without a game server to connect to, but so much depends on one that it's pretty pointless to try to do this without one.

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

> docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d redis postgres

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

> cd rcongui

> npm install

> npm start

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

> docker compose -f docker-compose.yml -f docker-compose.dev.yml build

> docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

Now test on http://localhost:8010

#### General notes:

If you have problems with dependancies or versions of python or nodejs please refer to the respective Dockerfile that can act as a guide on how to setup a development environment.

If you need a refresher on which process needs what variables have a look at the docker-compose.yml file.
