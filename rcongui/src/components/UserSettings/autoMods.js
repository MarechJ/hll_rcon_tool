import React from "react";
import UserSetting from ".";

export const LevelAutoMod = ({
  description,
  getEndpoint,
  setEndpoint,
  validateEndpoint,
  describeEndpoint,
}) => {
  const notes = `
    {
        /* 
            This auto-moderator has 2 features:
            1. Global server min/max level: No warning, players are kick after connection if they does'not match level requirements
            2. Min level by role: 3 steps, 1. warning via direct message (Y times), 2. punish (Z times) 3. kick
            Note that the state cycle for a given squad only resets once the rule-violation is fixed. So for example if you
            disabled the kick and have 3 punishes configured, once the 3 punishes are
            through that's it, nothing will happen anymore for that player if they still break level thresholds rules.
        
        */
        
        "enabled": false,

        /* Discord Webhook URL where audit logs should be sent. */
        "discord_webhook_url": null,

        /* 
            Announce that the server has managed level thresholds when at least one level thresholds rule is enabled.
            This message occurs only when a player connects to a server.
        */
        "announcement_enabled": true,

        /*
            Available fields: {min_level_msg} from min_level_message value,
            {max_level_msg} from max_level_message value, {level_thresholds_msg} from level_thresholds's message value
        */
        "announcement_message": "This server is under level thresholds control.\\n\\n{min_level_msg}{max_level_msg}{level_thresholds_msg}\\nThanks for understanding.",
        
        /*
            This is the message that will be used in the force kick without warnings when player does not match global level thresholds.
            The following variables are available to fill into the text: {player_name}, {squad_name} and {violation}
        */
        "force_kick_message": "You violated level thresholds rules on this server: {violation}.",
        
        /* 
            This allows to configure a global minimum level on the whole server and the matching kick message to display to players.
        */
        "min_level": 0,
        "min_level_message": "Access to this server is not allowed under level {level}",
        
        /*
            This allows to configure a global maximum level on the whole server and the matching kick message to display to players.
        */
        "max_level": 0,
        "max_level_message": "Access to this server is not allowed over level {level}",
        
        /*
            Violation message used as a description of the level thresholds violation when player is messaged, punished and kicked.
            Available properties: {role} matching label's value of previous map and {level} matching level's value from previous map.
        */
        "violation_message": "{role} are not allowed under level {level}",
        
        /*
            a map of roles to label, min_players & min_level that should not be taken by players under the required level only when min_players reached.
            Available roles are: 'armycommander', 'officer', 'antitank', 'automaticrifleman', 'assault', 'heavymachinegunner',
                'support', 'sniper', 'spotter', 'rifleman', 'crewman', 'tankcommander', 'engineer', 'medic'
            Label's values are used for sending messages to players.
            To disable, leave roles's value empty ie. "level_thresholds: {}"
        */
        "level_thresholds": {
            "armycommander": {
                "label": "Commander",
                "min_players": 0,
                "min_level": 50
            }
        }

        /*
            Step number 1
            Send a direct warning message to the players that violate level thresholds rules
            set to 0 to disable (this means it will move to punish directly), -1 for infinite warnings (will never go to punishes)
            set to 1 or Y to warn squad Y times before we move on to the punish step
        */
        "number_of_warnings": 2,

        /*
            This is the text that will be displayed to warn players.
            The following variables are available to fill into the text
            {player_name}, {received_warnings}, {max_warnings} and {next_check_seconds}, {violation}
        */
        "warning_message": "Warning, {player_name}! You violate level thresholds rules on this server: {violation}\\nYou will be punished after {max_warnings} warnings (you already received {received_warnings}), then kicked.\\nNext check will happen automatically in {next_check_seconds}s.",
        
        /*
            This is the number of seconds this auto-mod will wait until moving to
            the next warning or to the punish stage if the number_of_warning's is reached
        */
        "warning_interval_seconds": 60,

        /*
            Step number 2
            If the player still violates a level thresholds rule after
            the N warnings and the last warning_interval_seconds has elapsed, automod starts punishing
            Set to 0 to disable to punish entirely. I would advise setting warnings to infinity (-1) if you do that
            Set to -1 for infinite punish (will never go to kicks)
            Set to 1 or Z to apply Z punishes before we move to the next step (the kicks)
        */
        "number_of_punishments": 2,

        /*
            This is the message that will be used in the punish
            The following variables are available to fill into the text
            {player_name}, {received_punishes}, {max_punishes}, {next_check_seconds} and {violation}
        */
        "punish_message": "You violated level thresholds rules on this server: {violation}.\\nYou're being punished by a bot ({received_punishes}/{max_punishes}).\\nNext check in {next_check_seconds} seconds",
        
        /*
            This is the number of seconds to wait between punishes
            I wouldn't recommend setting a high value here (unless you chose infinite punishes) as once the player has died he has the opportunity to
            stop violating the level thresholds rules, so no excuse. Also it's even more frustrating to respawn run 300m and die again ;)
        */
        "punish_interval_seconds": 60,

        /*
            Step number 4
            Set the below value to false if you don't want to kick players after they reached the max amount of punishes
            note that if you disable punishes it will never go to that step. no matter if it's set to true
        */
        "kick_after_max_punish": true,
        /* After the Step 2 has reached it's max punishes, this is the amount of time in seconds the auto-mod will wait before kicking */
        "kick_grace_period_seconds": 120,
        
        /*
            This is the message that will be used in the kick
            The following variables are available to fill into the text
            {player_name}, {squad_name}, {kick_grace_period} and {violation}
        */
        "kick_message": "You violated level thresholds rules on this server: {violation}.\\nYour grace period of {kick_grace_period}s has passed.\\nYou failed to comply with the previous warnings."
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

export const NoLeaderAutoMod = ({
  description,
  getEndpoint,
  setEndpoint,
  validateEndpoint,
  describeEndpoint,
}) => {
  const notes = `
    {
        /*
            This auto-moderator has 4 steps, 1. internally noting (X times), 2. warning via direct message (Y times), 3. punish (Z times) 4. kick
            Note that the state cycle for a given squad only resets once it finally has an officer. So for example if you
            disabled the kick and have 3 punishes configured, once the 3 punishes are
            through that's it, nothing will happen anymore for that squad even if they still don't have an officer.

            Note 2: notes, warnings, punishes and kicks are tracked individual per player, not at the squad level.
            So if a player joins a squad that already received 3 punishes and will be kicked next, the new player will
            start at the first punish regardless (so he won't be kick)
            Set to true to enable the auto moderation of squads without officers

        */
        "enabled": false,

        /*
            If this is set to true no warning / punish / kick will be applied for real
            It turns the code into a "simulation" mode and only send what it would do to your discord audit log webhook
        */
        "dry_run": true,

        /* Discord Webhook URL where audit logs should be sent. */
        "discord_webhook_url": null,
        
        /*
            Step number 1
            If a squad has no officer all members are noted internally but no action is taken
            Since we sometimes receive wrong data from the game server we note those players
            and see if these squads still don't have an officer the next time we check
            set to 0 to disable (this means it will move to warn directly)
            set to 1 to X to note the squad X times before we move to the warn step (we recommend 1)
        */
        "number_of_notes": 1,

        /*
            This is the number of seconds this auto-mod will wait until moving to
            the next note or to warnings if the number_of_notes is reached
        */
        "notes_interval_seconds": 10,

        /*
            Deprecated: This option is deprecated and will be removed in a future release.
            Temporary message used as a warning text for player names that will lead to false-positives in auto-moderation,
            because of a game-server bug.
            See https://github.com/MarechJ/hll_rcon_tool/issues/117 for more details.
        */
        "whitespace_message": "Your name contains a whitespace at the end (because it is truncated as it is too long). Because of a bug in the game, you might suffer auto-moderation actions as a false-positive. Please change your name and restart your game to avoid this.",
        
        /*
            Step number 2
            Send a direct warning message to the squads that don't have an officer
            set to 0 to disable (this means it will move to punish directly), -1 for infinite warn
            set to 1 or Y to warn squad Y times before we move on to the punish step
        */
        "number_of_warnings": 2,

        /*
            This is the text that will be displayed to warn players.
            The following variables are available to fill into the text
            {player_name}, {squad_name}, {received_warnings}, {max_warnings} and {next_check_seconds}
        */
        "warning_message": "Warning, {player_name}! Your squad ({squad_name}) does not have an officer. Players of squads without an officer will be punished after {max_warnings} warnings (you already received {received_warnings}), then kicked.\\nNext check will happen automatically in {next_check_seconds}s.",
        
        /*
            This is the number of seconds this auto-mod will wait until moving to
            the next warning or to the punish if the number_of_warning's is reached
        */
        "warning_interval_seconds": 60,
    
        /*
            Step number 3
            If the squad still doesn't have an officer after
            the N warnings and the last warning_interval_seconds has elapsed, automod starts punishing
            Set to 0 to disable to punish entirely. I would advise setting warnings to infinity (-1) if you do that
            Set to -1 for infinite punish (will never go to kicks)
            Set to 1 or Z to apply Z punishes before we move to the next step (the kicks)
        */
        "number_of_punishments": 2,
        

        
        /*
            This is the number of seconds to wait between punishes (if the squad remains without an officer
            I wouldn't recommend setting a high value here (unless you chose infinite punishes) as once the player has died he has the opportunity to take
            the officer role, so no excuse. Also it's even more frustrating to respawn run 300m and die again ;)
        */
        "punish_interval_seconds": 40,

        /*
        This value will disable the punishes until the squad has at least the number of player set below
        So if you set min_squad_players_for_punish: 3 a squad of 2 will be immune to punishes (and kicks)
        */
        "min_squad_players_for_punish": 3,
        
        /*
        This option is the same as above but for the entire server. If the server has less players
        than the number you set below, not punish / kicks will be applied
        */
        "min_server_players_for_punish": 40,
        
        /*
            This is the message that will be used in the punish
            The following variables are available to fill into the text
            {player_name}, {squad_name}, {received_punishes}, {max_punishes} and {next_check_seconds}
        */
        "punish_message": "Your squad ({squad_name}) must have an officer.\\nYou're being punished by a bot ({received_punishes}/{max_punishes}).\\nNext check in {next_check_seconds} seconds",
        
        /*
            Step number 4
            Set the below value to false if you don't want to kick players after they reached the max amount of punishes
            note that if you disable punishes it will never go to that step. no matter if it's set to true 
        */
        "kick_after_max_punish": true,

        /* Same behavior as for the punishes, if the squad has less players than the below it won't kick */
        "min_squad_players_for_kick": 7,
        
        /* Same behavior as for the punishes, if the server has less players than the number below the auto-moderator will wait and not kick yet */
        "min_server_players_for_kick": 6,

        /* After the Step 2 has reached it's max punishes, this is the amount of time in seconds the auto-mod will wait before kicking */
        "kick_grace_period_seconds": 120,
        
        /*
            This is the message that will be used in the kick
            The following variables are available to fill into the text
            {player_name}, {squad_name} and {kick_grace_period}
        */
        "kick_message": "Your Squad ({squad_name}) must have an officer.\\nYour grace period of {kick_grace_period}s has passed.\\nYou failed to comply with the previous warnings.",
        
        /*
            You can define roles that are immune to punishes and kicks (this must be a list, the syntax is important)
            Available roles are: 'officer', 'antitank', 'automaticrifleman', 'assault', 'heavymachinegunner',
                'support', 'sniper', 'spotter', 'rifleman', 'crewman', 'tankcommander', 'engineer', 'medic'
        */
        "immune_roles": [],

        /* If the level of the player is below this number he/she will be immune to punishes / kicks */
        "immune_player_level": 15
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

export const SeedingAutoMod = ({
  description,
  getEndpoint,
  setEndpoint,
  validateEndpoint,
  describeEndpoint,
}) => {
  const notes = `
  {
    /*
        This auto-moderator has 3 steps, 1. warning via direct message (Y times), 3. punish (Z times) 4. kick

        Note that the state cycle for a given squad only resets once the rule-violation is fixed. So for example if you
        disabled the kick and have 3 punishes configured, once the 3 punishes are
        through that's it, nothing will happen anymore for that player if they still break seeding rules.
    */
    "enabled": false,

    /* Discord Webhook URL where audit logs should be sent. */
    "discord_webhook_url": null,

    /*
        Announce that the server is currently seeding when at least one seeding rule is enabled. When the player count exceeds
        the max_player settings of all seeding rules, the announcement is disabled automatically until the next round.

        This message occurs only when a player connects to a server. If the player count drops beneath the max_player setting of one
        seeding rule and a new map starts, all connected players will NOT get an announcement.
    */
    "announcement_enabled": false,

    /*
        {disallowed_roles}, {disallowed_roles_max_players}, {disallowed_weapons} and {disallowed_weapons_max_players}
        are the allowed message parameters
    */
    "announcement_message": "We are trying to populate the server! That means special rules apply.\\n\\n- {disallowed_roles} are not allowed (until {disallowed_roles_max_players} players are online)\\n- {disallowed_weapons} are not allowed (until {disallowed_weapons_max_players} players are online)\\n\\nThanks for understanding and helping us seed!",
    
    /*
        Step number 1
        
        Send a direct warning message to the players that violate seeding rules
        set to 0 to disable (this means it will move to punish directly), -1 for infinite warnings (will never go to punishes)
        set to 1 or Y to warn squad Y times before we move on to the punish step
    */
    "number_of_warnings": 2,

    /*
        {player_name}, {received_warnings}, {max_warnings}, {next_check_seconds} and {violation}
        are the allowed message parameters
    */
    "warning_message": "Warning, {player_name}! You violate seeding rules on this server: {violation}\nYou will be punished after {max_warnings} warnings (you already received {received_warnings}), then kicked.\nNext check will happen automatically in {next_check_seconds}s.",
    
    /*
        This is the number of seconds this auto-mod will wait until moving to
        the next warning or to the punish stage if the number_of_warning's is reached
    */
    "warning_interval_seconds": 60,
    
    /*
        Step number 2
        
        If the player still violates a seeding rule after
        the N warnings and the last warning_interval_seconds has elapsed, automod starts punishing
        
        Set to 0 to disable to punish entirely. I would advise setting warnings to infinity (-1) if you do that
        Set to -1 for infinite punish (will never go to kicks)
        Set to 1 or Z to apply Z punishes before we move to the next step (the kicks)
    */
    "number_of_punishments": 2,

    /*
        This is the message that will be used in the punish
        {player_name}, {received_punishes}, {max_punishes}, {next_check_seconds} and {violation}
        are the allowed message parameters
    */
    "punish_message": "You violated seeding rules on this server: {violation}.\nYou're being punished by a bot ({received_punishes}/{max_punishes}).\nNext check in {next_check_seconds} seconds",
    
    /*
        This is the number of seconds to wait between punishes
        I wouldn't recommend setting a high value here (unless you chose infinite punishes) as once the player has died he has the opportunity to
        stop violating the seeding rules, so no excuse. Also it's even more frustrating to respawn run 300m and die again ;)
    */
    "punish_interval_seconds": 60,
    
    /*
        Step number 4
        
        Set the below value to false if you don't want to kick players after they reached the max amount of punishes
        note that if you disable punishes it will never go to that step. no matter if it's set to true
    */
    "kick_after_max_punish": false,

    /* After the Step 2 has reached it's max punishes, this is the amount of time in seconds the auto-mod will wait before kicking */
    "kick_grace_period_seconds": 120,
    
    /*
        This is the message that will be used in the kick
        {player_name}, {squad_name} and {kick_grace_period}
        are the allowed message parameters
    */
    "kick_message": "You violated seeding rules on this server.\nYour grace period of {kick_grace_period}s has passed.\nYou failed to comply with the previous warnings.",
    
    /*
        The disallowed roles is a seeding rule that ultimately prevents players from taking a role that should generally not
        be used when a server has a playercount below a certain threshold (seeding).
    */
    "disallowed_roles": {

      /*
        the player count of the server needed for this rule to be enforced. The number is inclusive, which means, if you use 5
        this rule will be enforced for players 5 to max_players. If there are only 4 players on the server, the rules will
        not be enforced.
      */
      "min_players": 5,

      /*
        the player count of the server under which this rule should be enforced. The number is exclusive, which means, if you use 30
        this rule will be enforced for players 1 to 29, once the 30 player connected, the rule will not be enforced anymore.
      */
      "max_players": 30,

      /*
        a list of roles that should not be taken by players.
        Available roles are: 'officer', 'antitank', 'automaticrifleman', 'assault', 'heavymachinegunner', 
            'support', 'sniper', 'spotter', 'rifleman', 'crewman', 'tankcommander', 'engineer', 'medic'
      */
      "roles": {
        "tankcommander": "Tanks",
        "crewman": "Tanks"
      },

      /* 
        Violation message used as a description of the seeding violation when player is messaged, punished and kicked.
        {role} can be used in the message and will be filled with the players role
      */
      "violation_message": "{role} are not allowed when server is seeding"
    },

    /*
        The disallowed weapons is a seeding rule that prevents players from using defined weapons to kill other players. Different to the other
        automods, this rule does not use the escalation path (message -> punish -> kick) as configured in the general seeding automod config.
        Instead, players using one of the mentioned weapons (and given the server player count are in the bounds as configured) will be
        punished directly. This automod will also continue to punish players if they continue using disallowed weapons, even if they were punished
        already. The automod will not escalate to the kick stage, either.
    */
    "disallowed_weapons": {
      /*
        the player count of the server needed for this rule to be enforced. The number is inclusive, which means, if you use 5
        this rule will be enforced for players 5 to max_players. If there are only 4 players on the server, the rules will
        not be enforced.
      */
      "min_players": 5,

      /*
        the player count of the server under which this rule should be enforced. The number is exclusive, which means, if you use 30
        this rule will be enforced for players 1 to 29, once the 30 player connected, the rule will not be enforced anymore.
      */
      "max_players": 30,

      /*
        map of weapons players should not use. The key of the map is the weapon class as used by the game
        (https://gist.github.com/timraay/5634d85eab552b5dfafb9fd61273dc52#available-weapons),
        whereas the value of the map is a human friendly name of the weapon (as it will be passed
        to the {weapon} variable of the message parameter.
      */
      "weapons": {
            "155MM HOWITZER [M114]": "Artillery"
      },
      "violation_message": "{weapon} are not allowed when server is seeding"
    },


    "enforce_cap_fight": {
      /*
        the player count of the server needed for this rule to be enforced. The number is inclusive, which means, if you use 5
        this rule will be enforced for players 5 to max_players. If there are only 4 players on the server, the rules will
        not be enforced.
      */
      "min_players": 5,

      /*
        the player count of the server under which this rule should be enforced. The number is exclusive, which means, if you use 30
        this rule will be enforced for players 1 to 29, once the 30 player connected, the rule will not be enforced anymore.
      */
      "max_players": 30,

      /*
        The maximum number of caps a team can have while seeding. When a player gains offensive points while is team has
        this number of caps capped, they will be warned/punished by this automod.
      */
      "max_caps": 3,
      
      /*
        A boolean to indicate if this rule should go straight to punish the player (instead of warn them first). This might be valuable
        to enable, as the game will only refresh offensive points (which this rule is based upon) every minute. Capping a point takes 2 minutes in warfare mode.
        A player might get warnings, but the damage capping a point with "just" two warnings might justify directly punishing the player.
      */
      "skip_warning": false,
      "violation_message": "Attacking 4th cap while seeding is not allowed"
    }
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

export const NoSoloTankAutoMod = ({
  description,
  getEndpoint,
  setEndpoint,
  validateEndpoint,
  describeEndpoint,
}) => {
  const notes = `
      {
          /*
              This auto-moderator has 4 steps, 1. internally noting (X times), 2. warning via direct message (Y times), 3. punish (Z times) 4. kick
              Note that the state cycle for a given squad only resets once it finally has an officer. So for example if you
              disabled the kick and have 3 punishes configured, once the 3 punishes are
              through that's it, nothing will happen anymore for that squad even if they still don't have an officer.
  
              Note 2: notes, warnings, punishes and kicks are tracked individual per player, not at the squad level.
              So if a player joins a squad that already received 3 punishes and will be kicked next, the new player will
              start at the first punish regardless (so he won't be kick)
              Set to true to enable the auto moderation of squads without officers
  
          */
          "enabled": false,
  
          /*
              If this is set to true no warning / punish / kick will be applied for real
              It turns the code into a "simulation" mode and only send what it would do to your discord audit log webhook
          */
          "dry_run": true,
  
          /* Discord Webhook URL where audit logs should be sent. */
          "discord_webhook_url": null,
          
          /*
              Step number 1
              If a squad has no officer all members are noted internally but no action is taken
              Since we sometimes receive wrong data from the game server we note those players
              and see if these squads still don't have an officer the next time we check
              set to 0 to disable (this means it will move to warn directly)
              set to 1 to X to note the squad X times before we move to the warn step (we recommend 1)
          */
          "number_of_notes": 1,
  
          /*
              This is the number of seconds this auto-mod will wait until moving to
              the next note or to warnings if the number_of_notes is reached
          */
          "notes_interval_seconds": 10,
  
          /*
              Deprecated: This option is deprecated and will be removed in a future release.
              Temporary message used as a warning text for player names that will lead to false-positives in auto-moderation,
              because of a game-server bug.
              See https://github.com/MarechJ/hll_rcon_tool/issues/117 for more details.
          */
          "whitespace_message": "Your name contains a whitespace at the end (because it is truncated as it is too long). Because of a bug in the game, you might suffer auto-moderation actions as a false-positive. Please change your name and restart your game to avoid this.",
          
          /*
              Step number 2
              Send a direct warning message to the squads that don't have an officer
              set to 0 to disable (this means it will move to punish directly), -1 for infinite warn
              set to 1 or Y to warn squad Y times before we move on to the punish step
          */
          "number_of_warnings": 2,
  
          /*
              This is the text that will be displayed to warn players.
              The following variables are available to fill into the text
              {player_name}, {squad_name}, {received_warnings}, {max_warnings} and {next_check_seconds}
          */
          "warning_message": "Warning, {player_name}! Your squad ({squad_name}) does not have an officer. Players of squads without an officer will be punished after {max_warnings} warnings (you already received {received_warnings}), then kicked.\\nNext check will happen automatically in {next_check_seconds}s.",
          
          /*
              This is the number of seconds this auto-mod will wait until moving to
              the next warning or to the punish if the number_of_warning's is reached
          */
          "warning_interval_seconds": 60,
      
          /*
              Step number 3
              If the squad still doesn't have an officer after
              the N warnings and the last warning_interval_seconds has elapsed, automod starts punishing
              Set to 0 to disable to punish entirely. I would advise setting warnings to infinity (-1) if you do that
              Set to -1 for infinite punish (will never go to kicks)
              Set to 1 or Z to apply Z punishes before we move to the next step (the kicks)
          */
          "number_of_punishments": 2,
          
  
          
          /*
              This is the number of seconds to wait between punishes (if the squad remains without an officer
              I wouldn't recommend setting a high value here (unless you chose infinite punishes) as once the player has died he has the opportunity to take
              the officer role, so no excuse. Also it's even more frustrating to respawn run 300m and die again ;)
          */
          "punish_interval_seconds": 40,
  
          /*
          This value will disable the punishes until the squad has at least the number of player set below
          So if you set min_squad_players_for_punish: 3 a squad of 2 will be immune to punishes (and kicks)
          */
          "min_squad_players_for_punish": 3,
          
          /*
          This option is the same as above but for the entire server. If the server has less players
          than the number you set below, not punish / kicks will be applied
          */
          "min_server_players_for_punish": 40,
          
          /*
              This is the message that will be used in the punish
              The following variables are available to fill into the text
              {player_name}, {squad_name}, {received_punishes}, {max_punishes} and {next_check_seconds}
          */
          "punish_message": "Your squad ({squad_name}) must have an officer.\\nYou're being punished by a bot ({received_punishes}/{max_punishes}).\\nNext check in {next_check_seconds} seconds",
          
          /*
              Step number 4
              Set the below value to false if you don't want to kick players after they reached the max amount of punishes
              note that if you disable punishes it will never go to that step. no matter if it's set to true 
          */
          "kick_after_max_punish": true,
  
          /* Same behavior as for the punishes, if the squad has less players than the below it won't kick */
          "min_squad_players_for_kick": 7,
          
          /* Same behavior as for the punishes, if the server has less players than the number below the auto-moderator will wait and not kick yet */
          "min_server_players_for_kick": 6,
  
          /* After the Step 2 has reached it's max punishes, this is the amount of time in seconds the auto-mod will wait before kicking */
          "kick_grace_period_seconds": 120,
          
          /*
              This is the message that will be used in the kick
              The following variables are available to fill into the text
              {player_name}, {squad_name} and {kick_grace_period}
          */
          "kick_message": "Your Squad ({squad_name}) must have an officer.\\nYour grace period of {kick_grace_period}s has passed.\\nYou failed to comply with the previous warnings.",
          
          /*
              You can define roles that are immune to punishes and kicks (this must be a list, the syntax is important)
              Available roles are: 'officer', 'antitank', 'automaticrifleman', 'assault', 'heavymachinegunner',
                  'support', 'sniper', 'spotter', 'rifleman', 'crewman', 'tankcommander', 'engineer', 'medic'
          */
          "immune_roles": [],
  
          /* If the level of the player is below this number he/she will be immune to punishes / kicks */
          "immune_player_level": 15
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
