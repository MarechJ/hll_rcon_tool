import React from "react";
import UserSetting from ".";

export const AuditWebhooks = ({
  description,
  getEndpoint,
  setEndpoint,
  validateEndpoint,
  describeEndpoint,
}) => {
  const notes = `
    {
        /* 
            A list of Discord webhook URLs to send audit messages to, it's recommended to set this,
            so that kicks, bans, map changes, etc. will be shown in Discord

            You can set as many URLs as you want, but these are updated sequentially not concurrently,
            so setting more than one will delay the updates of each one and you should probably not
            set more than a few
        */
        "hooks": [
            {
                "url": "https://discord.com/api/webhooks/.../..."
            }
        ]
    }
    `;

  return (
    <UserSetting
      description={description}
      getEndpoint={getEndpoint}
      setEndpoint={setEndpoint}
      validateEndpoint={validateEndpoint}
      describeEndpoint={describeEndpoint}
      notes={notes}
    />
  );
};

export const AdminPingWebhooks = ({
  description,
  getEndpoint,
  setEndpoint,
  validateEndpoint,
  describeEndpoint,
}) => {
  const notes = `
    {
        /* 
            A list of Discord webhook URLs and user/role IDs to mention when one of \`trigger_words\` is used in game chat
            
            You can set as many URLs as you want, but these are updated sequentially not concurrently,
            so setting more than one will delay the updates of each one and you should probably not
            set more than a few
        */
        "hooks": [
            {
                "url": "https://discord.com/api/webhooks/.../...",

                /* A list of user ID(s), must be in the <@...> format */
                "user_mentions": [
                    "<@1234>"
                ],

                /* A list of role ID(s), must be in the <@&...> format */
                "role_mentions": [
                    "<@&1234>"
                ]
            }
        ],

        /*
            Comma-separated list of trigger words. Case-insensitive. Trigger words match whole words.
            "this is a TeSt message" would match trigger word "test"
            "this is a testmessage" would NOT match trigger word "test"
        */
        "trigger_words": [
            "!admin"
        ]
    }
    `;

  return (
    <UserSetting
      description={description}
      getEndpoint={getEndpoint}
      setEndpoint={setEndpoint}
      validateEndpoint={validateEndpoint}
      describeEndpoint={describeEndpoint}
      notes={notes}
    />
  );
};

export const CameraWebhooks = ({
  description,
  getEndpoint,
  setEndpoint,
  validateEndpoint,
  describeEndpoint,
}) => {
  const notes = `
    {
        /* 
            A list of Discord webhook URLs and user/role IDs to mention when a player enters admin camera

            You can set as many URLs as you want, but these are updated sequentially not concurrently,
            so setting more than one will delay the updates of each one and you should probably not
            set more than a few
        */
        "hooks": [
            {
                "url": "https://discord.com/api/webhooks/.../...",
                /* A list of user ID(s), must be in the <@...> format */
                "user_mentions": [
                    "<@1234>"
                ],
                /* A list of role ID(s), must be in the <@&...> format */
                "role_mentions": [
                    "<@&1234>"
                ]
            }
        ]
    }
    `;

  return (
    <UserSetting
      description={description}
      getEndpoint={getEndpoint}
      setEndpoint={setEndpoint}
      validateEndpoint={validateEndpoint}
      describeEndpoint={describeEndpoint}
      notes={notes}
    />
  );
};
export const WatchlistWebhooks = ({
  description,
  getEndpoint,
  setEndpoint,
  validateEndpoint,
  describeEndpoint,
}) => {
  const notes = `
    {
        /*
            A list of Discord webhook URLs and user/role IDs to mention when a watched player
            connects to the server

            You can set as many URLs as you want, but these are updated sequentially not concurrently,
            so setting more than one will delay the updates of each one and you should probably not
            set more than a few
        */
        "hooks": [
            {
                "url": "https://discord.com/api/webhooks/.../...",
                /* A list of user ID(s), must be in the <@...> format */
                "user_mentions": [
                    "<@1234>"
                ],
                /* A list of role ID(s), must be in the <@&...> format */
                "role_mentions": [
                    "<@&1234>"
                ]
            }
        ]
    }
    `;

  return (
    <UserSetting
      description={description}
      getEndpoint={getEndpoint}
      setEndpoint={setEndpoint}
      validateEndpoint={validateEndpoint}
      describeEndpoint={describeEndpoint}
      notes={notes}
    />
  );
};

/* TODO: update comments */
export const ChatWebhooks = ({
  description,
  getEndpoint,
  setEndpoint,
  validateEndpoint,
  describeEndpoint,
}) => {
  const notes = `
    {
        /*
            A list of Discord webhook URLs and user/role IDs to send in game chat to

            You can set as many URLs as you want, but these are updated sequentially not concurrently,
            so setting more than one will delay the updates of each one and you should probably not
            set more than a few
        */
        "hooks": [
            {
                "url": "https://discord.com/api/webhooks/1156773876626374778/qyXM1nlYRNU-6R6eaL1xCESqMyK2jnfT1L9N_USz9V05JZS7h6EwOkzGu0hHzyVx00QG"
            }
        ],

        /* Whether or not in game chat can @ mention Discord users/roles */
        "allow_mentions": true
    }
    `;

  return (
    <UserSetting
      description={description}
      getEndpoint={getEndpoint}
      setEndpoint={setEndpoint}
      validateEndpoint={validateEndpoint}
      describeEndpoint={describeEndpoint}
      notes={notes}
    />
  );
};
export const KillWebhooks = ({
  description,
  getEndpoint,
  setEndpoint,
  validateEndpoint,
  describeEndpoint,
}) => {
  const notes = `
    {
        /*
            A list of Discord webhook URLs to send kill/team kill messages to

            You can set as many URLs as you want, but these are updated sequentially not concurrently,
            so setting more than one will delay the updates of each one and you should probably not
            set more than a few
        */
        "hooks": [
            {
                "url": "https://discord.com/api/webhooks/.../..."
            }
        ],
        "send_kills": false,
        "send_team_kills": true
    }
    `;

  return (
    <UserSetting
      description={description}
      getEndpoint={getEndpoint}
      setEndpoint={setEndpoint}
      validateEndpoint={validateEndpoint}
      describeEndpoint={describeEndpoint}
      notes={notes}
    />
  );
};

export const LogLineWebhooks = ({
  description,
  getEndpoint,
  setEndpoint,
  validateEndpoint,
  describeEndpoint,
}) => {
  const notes = `
    {
        /*
            You can use this feature to subscribe to arbitrary log types and send them
            to Discord with optional messages.

            For example, you could mention roles or users in Discord when a match starts or ends.

            You can set as many URLs as you want, but these are updated sequentially not concurrently,
            so setting more than one will delay the updates of each one and you should probably not
            set more than a few
        */
        "webhooks": [
            /*
                A list of objects, each one can trigger off one or more log types,
                and has a webhook and optional user/role IDs to mention
            */
            {
                /* A list of log types to send to Discord */
                "log_types": [
                    "CHAT[Axis][Unit]",
                    "MATCH ENDED"
                ],
                "webhook": {
                    "url": "https://discord.com/api/webhooks/.../...",
                    /* A list of user ID(s), must be in the <@...> format to mention*/
                    "user_mentions": [
                        "<@432>",
                        "<@4321>"
                    ],
                    /* A list of role ID(s), must be in the <@...> format  to mention*/
                    "role_mentions": []
                }
            }
        ]
    }
    `;

  return (
    <UserSetting
      description={description}
      getEndpoint={getEndpoint}
      setEndpoint={setEndpoint}
      validateEndpoint={validateEndpoint}
      describeEndpoint={describeEndpoint}
      notes={notes}
    />
  );
};
