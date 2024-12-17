const ChatCommandsNotes = `
  {
    "enabled": false,

    /* A list of commands, their trigger words, the message to send to the player and a description */
    "command_words": [
      {
        /* Only ! or @ are valid command prefixes */
        "words": [
          "!wkm",
          "@wkm"
        ],
        "message": "You were last killed by {last_nemesis_name} with {last_nemesis_weapon}",
        /* A short description of what the command does for the 'describe_words' commands */
        "description": "Who killed me"
      },
      {
        "words": [
          "!discord"
        ],
        "message": "You can join our discord at {discord_invite_url}",
        "description": "Discord invite"
      }
    ],
    /* A list of commands that will send a description of all commands to the player */
    "describe_words": [
      "!help",
      "@help"
    ]
  }
  `

  export default ChatCommandsNotes;