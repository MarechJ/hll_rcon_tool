# User Guide

This guide contains information on how to use certain features of the app.
The guide is incomplete and will be expanded in the future.

## Table Of Contents

* [Discord Integration](#Discord-Integration)
* [Introduction to Balancing/Shuffling](#balancing--shuffling-teams)
    * [Logging](#logging)
    * [Webhook](#webhooks)
    * [Balancing Team Sizes](#team-size-balancing)
    * [Shuffling Teams](#shuffling)

## Discord Integration

The app is able to forward in-game chat messages and kill log into your
Discord server through Discord webhooks.

To enable Discord Integration features, we'll have to edit the `.env` file
and fill in the custom values for your Discord server.
We're interested in the lines starting with `DISCORD_` in the `.env` file.
Read through the comments above these lines. Comments are the lines starting with `#`.

###### Creating a webhook.

1. Navigate to the channel settings.

    ![editing channel settings](images/userguide_discord_edit_channel.png)

2. Create a webhook.

    ![creating a webhook](images/userguide_discord_create_webhook.png)
    
3. Copy webhook URL.

    ![copying webhook url](images/userguide_discord_copy_webhook_url.png)

###### Finding role IDs.

1. Enable Developer Mode in Discord User Setting.

    ![advanced mode](images/userguide_discord_advanced_mode.png)
    
2. Copy desired role ID(s).

    ![copying role ID](images/userguide_discord_get_copy_role_id.png)

## Balancing / Shuffling Teams

Stacked teams is a contentious topic in Hell Let Loose. Server admins have limited options to help balance such as asking their communities to self regulate, or manually swapping players. This feature provides some features for admins to shuffle teams in various ways, or to even out team size imbalances.

**Please note** that you can only run this command every 5 seconds, and that it will take several seconds for RCON to finish swapping players. Please be mindful when trying to run this multiple times in quick succession.

### Logging

This feature includes a `team_balance` log that you can find with your other RCON server logs.

### Webhooks

This feature includes an **optional** webhook `DISCORD_BALANCE_SHUFFLE_WEBHOOK` that you can set in your `.env` file to direct audit messages to. Player swaps and running either method is already directed to the `DISCORD_WEBHOOK_AUDIT_LOG` if set, so this is fairly redundant. However this does provide a way for you to easily see a filtered view of what swaps you have run and what players were swapped, as well as expose the information to your community without having to share all of your RCON actions.

**Please note** that swapping players, especially large number of players may upset your player base and cause them to leave your server.  At the moment **neither of these swap options take squad membership into consideration.** Players who are with their friends who end up on opposite teams may simply leave your server.  **Shuffle at your own risk.**

Also please note that this is not guaranteed to be bug free, I have made a considered effort to iron out bugs and test it, but **shuffle at your own risk.**

### Team Size Balancing

The team balance feature solves the problem of team sizes being unequal for various reasons (such as after map changes). Admins can at the click of a button even out team sizes while filtering which players are considered as described below.

Players are first filtered by the chosen options below and then the number of players needed to even teams are swapped by the selected method. **Please note** that if you are too strict with your criteria you may have too few people available to swap and the team sizes may still be uneven.

**Please note** that the game server will always assign teamless players to the Allied team first, so they will be swapped **twice** if they are sent to the Axis team.

Player Selection Criteria
* Swap on Death
   * By default players are swapped **immediately** select this if you would prefer to swap players on death. **Please note** that if you choose to swap on death team sizes may still be dramatically different depending on how quickly swapped players die.
* Include Teamless Players
   * Whether or not players who are on the server but have not joined a team are considered for swapping.
* Immune Roles
   * Players who have a selected role will not be swapped. Can be used to prevent the commander, tank crew, recon, etc. from being swapped. **Please note** that players that are not on a team have the `rifleman` role, if you make `rifleman` immune it will impact your ability to swap teamless players.
* Immune Levels
   * Players whose level is <= this will not be swapped. Can be used to avoid swapping newer players.
* Immune Seconds
   * The amount of time that must pass before a player who has been swapped can be swapped in a future swap. Useful if you need to run the command multiple times to get equitable team sizes, but don't want to swap the same people too quickly. **This time is only set when the player is swapped by either this team balancing commmand, or by the shuffle command. It is not set if a player changes teams themselves or they are manually swapped in RCON.**

After filtering based on the above criteria the number of players needed to even teams (for instance in a 40 v 20 situation 10 players would need to be switched) are selected
by one of the methods below. If there are insufficient players, all the available players will be swapped but team sizes will still be uneven.

Swap Methods
* Most Recently Arrived
   * Players who connected to the server more recently are chosen before others who joined later.
* Least Recently Arrived
   * Players who have been on the server the longest are chosen before those who joined more recently.
* Randomly
   * Players are selected at random. 

### Shuffling

The team shuffle feature provides server admins some tools to shuffle teams that are dramatically unbalanced due to skill level, or provide the ability to randomize teams for custom events, etc. All of these methods are **guaranteed** to keep team sizes equitable (no more than 1 player difference in team sizes) unless there is an error, but the team that was originally larger is not guaranteed to stay the largest after the shuffle.

**Please note** that for all shuffle methods, which faction (Axis or Allied) players are swapped to first is randomly selected to avoid faction bias.

**Please note** that the entire server (to include teamless players) are considered regardless of any criteria that you have selected for team balancing.

* Split Shuffle
   * This will randomly select half of each team and swap them to the opposite team.
* Random Shuffle
   * Randomly shuffle the entire server, every player has an equal chance to be swapped to the opposite team.
* By Player Level
   * Players are sorted by their level and then distributed to whichever team has the lowest mean player level, or to the smaller team if team sizes are not equal.  **Please note** that player skill is not a super great judge of skill, or a good judge of who will build spawns and defend objectives.