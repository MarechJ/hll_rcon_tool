# User Guide

This guide contains information on how to use certain features of the app.
The guide is incomplete and will be expanded in the future.

## Table Of Contents

* [Discord Integration](#Discord-Integration)

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
