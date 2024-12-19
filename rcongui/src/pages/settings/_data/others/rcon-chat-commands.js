const RconChatCommandsNotes = `
  {
    "enabled": false,
  
    /* A list of commands, their trigger words, the rcon commands to execute and a description */
    "command_words": [
      {
        /* Only ! or @ are valid command prefixes */
        "words": [
          "!switch",
          "@switch"
        ],
        /* Can hold a list of commands that should be executed (in an undefined order). The syntax is the same as in AutoSettings commands. */
        "commands": {
          "switch_player_now": {
            /* Parameters of the command to execute, see the API documentation (/api/get_api_documentation) for possible parameters */
            /* Parameter values can have context parameters replace. Context parameters are things like player_name or player_id of the player issuing the command. */
            "player_name": "{player_name}"
          }
        },
        /* Whether the command is enabled or not (true == enabled) */
        "enabled": false,
        /* A short description of what the command does for the 'describe_words' commands */
        "description": "Switch yourself in side"
      },
      {
        "words": [
          "!admin"
        ],
        "message": null,
        "command": {
          "add_admin": {
            "role": "junior",
            "player_id": "{player_id}",
            "description": "{player_name}"
          }
        },
        "enabled": false,
        "description": "Add yourself to admin cam list"
      }
    ],
    /* A list of commands that will send a description of all commands to the player */
    "describe_words": [
      "!help",
      "@help"
    ]
  }
  `

export default RconChatCommandsNotes
