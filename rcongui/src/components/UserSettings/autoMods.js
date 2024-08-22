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
                This automod has 2 features:
                1. Global server min/max level :
                - No warning, players are kick after connection if they don't match level requirements.
                2. Min level by role (3 steps) :
                - 2.1. warning via direct message (Y times) ;
                - 2.2. punish (Z times) ;
                - 2.3. kick.

                Note :
                The state cycle for a given player only resets once the rule-violation is fixed.
                So, for example, if you disabled the kick and have 3 punishes configured,
                once the 3 punishes are through, that's it : nothing will happen anymore to the players,
                even if they still break level thresholds rules.
            */
            "enabled": false,

            /*
                If this is set to true, NO warning / punish / kick will be applied for real.
                It turns the code into a "simulation" mode
                and only send what it would do to your Discord audit log webhook.
            */
            "dry_run": false,

            /*
                Discord Webhook URL where audit logs should be sent.
            */
            "discord_webhook_url": null,

            /*
                This is either an empty list [], or a list of flags
                to exempt a player from this automod features.
                To use, add a flag or multiple flags to the list,
                then flag the players you want to exempt in the CRCON UI.
            */
            "whitelist_flags": [
                "🚨"
            ],

            /*
                If the "enabled" parameter above is set to "true",
                the automod won't do anythying below this number of players on the server.
                - set to 0 if you want the automod to be always active,
                regardless the number of players.
            */
            "dont_do_anything_below_this_number_of_players": 0,

            /* 
                Announce that the server has managed level thresholds
                when at least one level thresholds rule is enabled.
                This message occurs only once, when a player connects to the server.
            */
            "announcement_enabled": false,

            /*
                Only make the announce to players that are impacted by the level thresholds rules.
            */
            "only_announce_impacted_players": true,

            /*
                The following variables are available :
                - {min_level_msg} from min_level_message value ;
                - {max_level_msg} from max_level_message value ;
                - {level_thresholds_msg} from level_thresholds's message value
            */
            "announcement_message": "This server is under level thresholds control.\\n\\n{min_level_msg}{max_level_msg}{level_thresholds_msg}\\nThanks for understanding.",

            /*
                Step 1 of 3
                Send a direct warning message to the players that violate level thresholds rules.
                - set to 0 to disable (directly move to punish step) ;
                - set to -1 for infinite warnings (will never go to punish step) ;
                - set to 1 or Y to warn squad Y times before moving to punish step.
                Recommended : 2
            */
            "number_of_warnings": 2,

            /*
                This is the number of seconds until moving to the next warning
                (or to the punish step if 'number_of_warnings' is reached).
                Recommended : 60
            */
            "warning_interval_seconds": 60,

            /*
                The following variables are available :
                - {player_name} ;
                - {squad_name} ;
                - {received_warnings} ;
                - {max_warnings} ;
                - {next_check_seconds}.
            */
            "warning_message": "Warning, {player_name}! You violate level thresholds rules on this server: {violation}\\nYou will be punished after {max_warnings} warnings (you already received {received_warnings}), then kicked.\\nNext check will happen automatically in {next_check_seconds}s.",

            /*
                Step 2 of 3
                Start punishing if the player still violates a level thresholds rule
                after 'number_of_warnings' * 'warning_interval_seconds'
                - set to 0 to disable to punish step entirely.
                - set to -1 for infinite punishes (will never go to kick step) ;
                - set to Z to apply Z punishes before moving to kick step.
                Recommended : 2
                Advice : set 'number_of_warnings' to -1 if you set this to 0.
            */
            "number_of_punishments": 2,

            /*
                Disable the punishes until the squad has at least this number of players.
                ie : if you set 3, a squad of 2 will be immune to punishes (and kicks).
            */
            "min_squad_players_for_punish": 0,

            /*
                This option is the same as above, but for the entire server.
                If the server has less players than the number you set below,
                no punishes / kicks will be applied.
            */
            "min_server_players_for_punish": 0,

            /*
                This is the number of seconds to wait between punishes.
                Recommended : 60
            */
            "punish_interval_seconds": 60,

            /*
                The following variables are available :
                - {player_name} ;
                - {received_punishes} ;
                - {max_punishes} ;
                - {next_check_seconds} ;
                - {violation}.
            */
            "punish_message": "You violated level thresholds rules on this server: {violation}.\\nYou're being punished by a bot ({received_punishes}/{max_punishes}).\\nNext check in {next_check_seconds} seconds",

            /*
                Step 3 of 3
                Note :
                If you have set 'number_of_punishments' to -1 or 0,
                it will never reach that step.
                - set to 'false' if you don't want to kick players after they reached 'number_of_punishments'.
                Advice : set 'number_of_punishments' to -1 if you set this to 'false'.
            */
            "kick_after_max_punish": true,

            /*
                Same behavior as for the punishes :
                if the squad has less players than this, automod won't kick.
                ie : if you set 3, a squad of 2 will be immune to kicks.
            */
            "min_squad_players_for_kick": 0,

            /*
                Same behavior as for the punishes :
                kick step is disabled if the server has less players than this.
            */
            "min_server_players_for_kick": 0,

            /*
                Number of seconds to wait before kicking,
                after 'number_of_punishments' has been reached
            */
            "kick_grace_period_seconds": 60,

            /*
                The following variables are available :
                - {player_name} ;
                - {squad_name} ;
                - {kick_grace_period} ;
                - {violation}.
            */
            "kick_message": "You violated level thresholds rules on this server: {violation}.\\nYour grace period of {kick_grace_period}s has passed.\\nYou failed to comply with the previous warnings.",

            /*
                This is the message that will be used in the force kick without warnings
                when player does not match global level thresholds.
                The following variables are available :
                - {player_name} ;
                - {squad_name} ;
                - {violation}.
            */
            "force_kick_message": "You violated level thresholds rules on this server: {violation}.",

            /* 
                This allows to configure a global minimum level on the whole server
                and the matching kick message to display to players.
                - set 'min_level' to 0 to disable.
            */
            "min_level": 0,
            "min_level_message": "Access to this server is not allowed under level {level}",

            /*
                This allows to configure a global maximum level on the whole server
                and the matching kick message to display to players.
                - set 'max_level' to 0 to disable.
            */
            "max_level": 0,
            "max_level_message": "Access to this server is not allowed over level {level}",

            /*
                Violation message used as a description of the level thresholds violation
                when player is messaged, punished and kicked.
                Available properties:
                - {role} matching label's value of previous map
                - {level} matching level's value from previous map.
            */
            "violation_message": "{role} are not allowed under level {level}",

            /*
                Enable ('true') or disable ('false') the protection against "level 1 bug" :
                due to a missed synchro between Steam and the game server,
                any player can log in as level 1, no matter their real level.
                They could then be punished if violating level rules.
                - set to 'true' to immune level 1 players from warn/punishes/kicks.
                Recommended : false (this bug seems to have disappeared since 2023)
            */
            "levelbug_enabled": false,

            /*
                Restricts access to roles when :
                player's level is below 'min_level' AND server's players count is >= 'min_players'.
                Available roles :
                    'armycommander', 'officer', 'antitank', 'automaticrifleman', 'assault', 'heavymachinegunner',
                    'support', 'sniper', 'spotter', 'rifleman', 'crewman', 'tankcommander', 'engineer', 'medic'.
                Label's values are the roles translations in your language.
                - To disable, leave roles's value empty. ie. "level_thresholds: {}"
                - To enable level enforcement at all times, set 'min_players' at 0.
            */
            "level_thresholds": {
                "armycommander": {
                    "label": "Commander",
                    "min_players": 0,
                    "min_level": 50
                }
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
                This automod has 4 steps :
                - 1. internally noting (X times) ;
                - 2. warning via direct message (Y times) ;
                - 3. punish (Z times) ;
                - 4. kick

                Note :
                The state cycle for a given squad only resets once it finally has an officer.
                So, for example, if you disabled the kick and have 3 punishes configured,
                once the 3 punishes are through, that's it : nothing will happen anymore for that squad,
                even if they still don't have an officer.

                Note 2:
                notes, warnings, punishes and kicks are tracked per player, not at the squad level.
                So if a player joins a squad that already received 3 punishes and will be kicked next,
                the new player will start at the first punish (so he won't be kick).
            */
            "enabled": false,

            /*
                If this is set to true, NO warning / punish / kick will be applied for real.
                It turns the code into a "simulation" mode
                and only send what it would do to your Discord audit log webhook.
            */
            "dry_run": false,

            /*
                Discord Webhook URL where audit logs should be sent.
            */
            "discord_webhook_url": null,

            /*
                This is either an empty list [], or a list of flags
                to exempt a player from this automod features.
                To use, add a flag or multiple flags to the list,
                then flag the players you want to exempt in the CRCON UI.
            */
            "whitelist_flags": [
                "🚨"
            ],

            /*
                Roles that are immune to punishes and kicks
                (this must be a list, the syntax is important)
                Available roles are : 'armycommander', 'officer', 'rifleman', 'assault',
                'automaticrifleman', 'medic', 'support', 'heavymachinegunner', 'antitank',
                'engineer', 'tankcommander', 'crewman', 'spotter', 'sniper'

                Example :
                    "immune_roles": [
                        "armycommander",
                        "medic"
                    ],
            */
            "immune_roles": [],

            /*
                If the player's level is below this number,
                he/she will be immune to punishes and kicks.
                - set to 0 to disable.
            */
            "immune_player_level": 0,

            /*
                If the "enabled" parameter above is set to "true",
                the automod won't do anythying below this number of players on the server.
                - set to 0 if you want the automod to be always active,
                regardless the number of players.
            */
            "dont_do_anything_below_this_number_of_players": 0,

            /*
                Step 1 of 4
                If a squad has no officer all members are noted internally but no action is taken.
                Since we sometimes receive wrong data from the game server, we note those players
                and see if these squads still don't have an officer the next time we check.
                - set to 0 to disable (it will directly move to warn) ;
                - set to 1 to X to note the squad X times before moving to the warning step.
                Recommended : 1
            */
            "number_of_notes": 1,

            /*
                This is the number of seconds to wait until moving to the next note
                (or to the warning step if 'number_of_notes' is reached).
                Recommended : 10
            */
            "notes_interval_seconds": 10,

            /*
                Step 2 of 4
                Send a direct warning message to the squads that don't have an officer.
                - set to 0 to disable (directly move to punish step) ;
                - set to -1 for infinite warnings (will never go to punish step) ;
                - set to 1 or Y to warn squad Y times before moving to punish step.
                Recommended : 2
            */
            "number_of_warnings": 2,

            /*
                This is the number of seconds until moving to the next warning
                (or to the punish step if 'number_of_warnings' is reached).
                Recommended : 60
            */
            "warning_interval_seconds": 60,

            /*
                The following variables are available :
                - {player_name} ;
                - {squad_name} ;
                - {received_warnings} ;
                - {max_warnings} ;
                - {next_check_seconds}.
            */
            "warning_message": "Warning, {player_name}! Your squad ({squad_name}) does not have an officer. Players of squads without an officer will be punished after {max_warnings} warnings (you already received {received_warnings}), then kicked.\\nNext check will happen automatically in {next_check_seconds}s.",
        
            /*
                Step 3 of 4
                Starts punishing if the squad still doesn't have an officer
                after 'number_of_warnings' * 'warning_interval_seconds'
                - set to 0 to disable to punish entirely ;
                - set to -1 for infinite punish (will never go to kick step) ;
                - set to Z to apply Z punishes before moving to kick step.
                Recommended : 2
                Advice : set 'number_of_warnings' to -1 if you set this to 0.
            */
            "number_of_punishments": 2,

            /*
                Disable the punishes until the squad has at least this number of players.
                ie : if you set 3, a squad of 2 will be immune to punishes (and kicks).
            */
            "min_squad_players_for_punish": 0,
        
            /*
                This option is the same as above, but for the entire server.
                If the server has less players than the number you set below,
                no punishes / kicks will be applied.
            */
            "min_server_players_for_punish": 0,

            /*
                This is the number of seconds to wait between punishes.
                Recommended : 60
            */
            "punish_interval_seconds": 60,

            /*
                The following variables are available :
                - {player_name} ;
                - {squad_name} ;
                - {received_punishes} ;
                - {max_punishes} ;
                - {next_check_seconds}.
            */
            "punish_message": "Your squad ({squad_name}) must have an officer.\\nYou're being punished by a bot ({received_punishes}/{max_punishes}).\\nNext check in {next_check_seconds} seconds",

            /*
                Step 4 of 4
                Note :
                If you have set 'number_of_punishments' to -1 or 0,
                it will never reach that step.
                - set to 'false' if you don't want to kick players after they reached 'number_of_punishments'.
                Advice : set 'number_of_punishments' to -1 if you set this to 'false'.
            */
            "kick_after_max_punish": true,

            /*
                Same behavior as for the punishes :
                kick is disabled if the squad has less players than this.
                ie : if you set 3, a squad of 2 will be immune to kicks.
            */
            "min_squad_players_for_kick": 0,
        
            /*
                Same behavior as for the punishes :
                kick step is disabled if the server has less players than this.
            */
            "min_server_players_for_kick": 0,

            /*
                Number of seconds to wait before kicking,
                after 'number_of_punishments' has been reached
            */
            "kick_grace_period_seconds": 60,
        
            /*
                The following variables are available :
                - {player_name} ;
                - {squad_name} ;
                - {kick_grace_period}.
            */
            "kick_message": "Your Squad ({squad_name}) must have an officer.\\nYour grace period of {kick_grace_period}s has passed.\\nYou failed to comply with the previous warnings.",
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
                This automod has 3 steps:
                - 1. warning via direct message (Y times) ;
                - 2. punish (Z times) ;
                - 3. kick

                Note that the state cycle for a given player only resets once the rule-violation is fixed.
                So, for example, if you disabled the kick and have 3 punishes configured,
                once the 3 punishes are through that's it, nothing will happen anymore for that player,
                even if they still break seeding rules.
            */
            "enabled": false,

            /*
                If this is set to true, NO warning / punish / kick will be applied for real.
                It turns the code into a "simulation" mode
                and only send what it would do to your Discord audit log webhook.
            */
            "dry_run": false,

            /*
                Discord Webhook URL where audit logs should be sent.
            */
            "discord_webhook_url": null,

            /*
                This is either an empty list [], or a list of flags
                to exempt a player from this automod features.
                To use, add a flag or multiple flags to the list,
                then flag the players you want to exempt in the CRCON UI.
            */
            "whitelist_flags": [
                "🚨"
            ],

            /*
                Roles that are immune to punishes and kicks
                (this must be a list, the syntax is important)
                Available roles are : 'armycommander', 'officer', 'rifleman', 'assault',
                'automaticrifleman', 'medic', 'support', 'heavymachinegunner', 'antitank',
                'engineer', 'tankcommander', 'crewman', 'spotter', 'sniper'

                Example :
                    "immune_roles": [
                        "armycommander",
                        "medic"
                    ],
            */
            "immune_roles": [],

            /*
                If the player's level is below this number,
                he/she will be immune to punishes and kicks.
                - set to 0 to disable.
            */
            "immune_player_level": 0,

            /*
                If the "enabled" parameter above is set to "true",
                the automod won't do anythying below this number of players on the server.
                - set to 0 if you want the automod to be always active,
                regardless the number of players.
            */
            "dont_do_anything_below_this_number_of_players": 0,

            /*
                Announce that the server is currently seeding
                when at least one seeding rule is enabled.
                When the player count exceeds the max_player settings of all seeding rules,
                the announcement is automatically disabled until the next round.

                This message occurs only once, when the player connects to the server.
                If the players count drops beneath the max_player setting of one seeding rule and a new map starts,
                connected players will NOT get another announcement.
            */
            "announcement_enabled": false,

            /*
                The following variables are available :
                - {disallowed_roles} ;
                - {disallowed_roles_max_players} ;
                - {disallowed_weapons} ;
                - {disallowed_weapons_max_players}.
            */
            "announcement_message": "We are trying to populate the server! That means special rules apply.\\n\\n- {disallowed_roles} are not allowed (until {disallowed_roles_max_players} players are online)\\n- {disallowed_weapons} are not allowed (until {disallowed_weapons_max_players} players are online)\\n\\nThanks for understanding and helping us seed!",
    
            /*
                Step 1 of 3
                Send a direct warning message to the players that violate seeding rules.
                - set to 0 to disable (directly move to punish step) ;
                - set to -1 for infinite warnings (will never go to punish step) ;
                - set to 1 or Y to warn squad Y times before moving to punish step.
                Recommended : 2
            */
            "number_of_warnings": 2,

            /*
                This is the number of seconds until moving to the next warning
                (or to the punish step if 'number_of_warnings' is reached).
                Recommended : 60
            */
            "warning_interval_seconds": 60,

            /*
                The following variables are available :
                - {player_name} ;
                - {received_warnings} ;
                - {max_warnings} ;
                - {next_check_seconds} ;
                - {violation}.
            */
            "warning_message": "Warning, {player_name}! You violate seeding rules on this server: {violation}\\nYou will be punished after {max_warnings} warnings (you already received {received_warnings}), then kicked.\\nNext check will happen automatically in {next_check_seconds}s.",
    
            /*
                Step 2 of 3
                Start punishing if the player still violates a seeding rule
                after 'number_of_warnings' * 'warning_interval_seconds'
                - set to 0 to disable to punish step entirely.
                - set to -1 for infinite punishes (will never go to kick step) ;
                - set to Z to apply Z punishes before moving to kick step.
                Recommended : 2
                Advice : set 'number_of_warnings' to -1 if you set this to 0.
            */
            "number_of_punishments": 2,

            /*
                Disable the punishes until the squad has at least this number of players.
                ie : if you set 3, a squad of 2 will be immune to punishes (and kicks).
            */
            "min_squad_players_for_punish": 0,
        
            /*
                This option is the same as above, but for the entire server.
                If the server has less players than the number you set below,
                no punishes / kicks will be applied.
            */
            "min_server_players_for_punish": 0,

            /*
                This is the number of seconds to wait between punishes.
            */
            "punish_interval_seconds": 60,

            /*
                The following variables are available :
                - {player_name} ;
                - {received_punishes} ;
                - {max_punishes} ;
                - {next_check_seconds} ;
                - {violation}.
            */
            "punish_message": "You violated seeding rules on this server: {violation}.\\nYou're being punished by a bot ({received_punishes}/{max_punishes}).\\nNext check in {next_check_seconds} seconds",
    
            /*
                Step 3 of 3
                Note :
                If you have set 'number_of_punishments' to -1 or 0,
                it will never reach that step.
                - set to 'false' if you don't want to kick players after they reached 'number_of_punishments'.
                Advice : set 'number_of_punishments' to -1 if you set this to 'false'.
            */
            "kick_after_max_punish": true,

            /*
                Same behavior as for the punishes :
                if the squad has less players than this, automod won't kick.
                ie : if you set 3, a squad of 2 will be immune to kicks.
            */
            "min_squad_players_for_kick": 0,
        
            /*
                Same behavior as for the punishes :
                kick step is disabled if the server has less players than this.
            */
            "min_server_players_for_kick": 0,

            /*
                Number of seconds to wait before kicking,
                after 'number_of_punishments' has been reached
            */
            "kick_grace_period_seconds": 60,
    
            /*
                The following variables are available :
                - {player_name} ;
                - {squad_name} ;
                - {kick_grace_period}.
            */
            "kick_message": "You violated seeding rules on this server.\\nYour grace period of {kick_grace_period}s has passed.\\nYou failed to comply with the previous warnings.",
    
            /*
                The disallowed roles is a seeding rule that ultimately prevents players from taking a role that should generally not
                be used when a server has a playercount below a certain threshold (seeding).
            */
            "disallowed_roles": {
                /*
                    Don't enforce the rule until this server's players count is reached.
                    The number is inclusive.
                    ie : if you use 5, these rules will be enforced from 5 connected players, up to 'max_players'.
                    If there are only 4 players on the server, these rules will NOT be enforced.
                */
                "min_players": 0,

                /*
                    Stop enforcing the rule if this server's players count is reached.
                    The number is exclusive.
                    ie : if you use 30, this rule will be enforced for players 1 to 29,
                    once the 30th player has connected, this rule will NOT be enforced anymore.
                */
                "max_players": 100,

                /*
                    Roles that should NOT be taken by players during seed :
                    Available roles are :
                    'officer', 'antitank', 'automaticrifleman', 'assault', 'heavymachinegunner', 'support',
                    'sniper', 'spotter', 'rifleman', 'crewman', 'tankcommander', 'engineer', 'medic'
                */
                "roles": {
                    "tankcommander": "Tank commander",
                    "crewman": "Tank crewman"
                },

                /* 
                    Violation message used as a description of the seeding violation when player is messaged, punished and kicked.
                    {role} can be used in the message and will be filled with the players role.
                */
                "violation_message": "{role} are not allowed when server is seeding",
            },

            /*
                The disallowed weapons is a seeding rule that prevents players from using defined weapons to kill other players.
                Different to the other automods, this rule does not use the escalation path (message -> punish -> kick) as configured in the general seeding automod config.
                Instead, players using one of these weapons (and given the server player count are in the bounds as configured)
                will be directly punished.
                This automod will also continue to punish players if they continue using disallowed weapons,
                even if they were punished already.
                The automod will not escalate to the kick step, either.
            */
            "disallowed_weapons": {
                /*
                    Don't enforce the rule until this server's players count is reached.
                    The number is inclusive.
                    ie : if you use 5, these rules will be enforced from 5 connected players, up to 'max_players'.
                    If there are only 4 players on the server, the rules will NOT be enforced.
                */
                "min_players": 0,

                /*
                    Stop enforcing the rule if this server's players count is reached.
                    The number is exclusive.
                    ie : if you use 30, this rule will be enforced for players 1 to 29,
                    once the 30th player has connected, this rule will NOT be enforced anymore.
                */
                "max_players": 100,

                /*
                    map of weapons players should not use.
                    The key of the map is the weapon class as used by the game
                    (https://gist.github.com/timraay/5634d85eab552b5dfafb9fd61273dc52#available-weapons),
                    whereas the value of the map is a human friendly name of the weapon
                    (as it will be passed to the {weapon} variable of the message parameter.
                */
                "weapons": {
                    "155MM HOWITZER [M114]": "Artillery"
                },
                "violation_message": "Using {weapon} is not allowed when server is seeding."
            },

            "enforce_cap_fight": {
                /*
                    Don't enforce the rule until this server's players count is reached.
                    The number is inclusive.
                    ie : if you use 5, these rules will be enforced from 5 connected players, up to 'max_players'.
                    If there are only 4 players on the server, the rules will NOT be enforced.
                */
                "min_players": 0,

                /*
                    Stop enforcing the rule if this server's players count is reached.
                    The number is exclusive.
                    ie : if you use 30, this rule will be enforced for players 1 to 29,
                    once the 30th player has connected, this rule will NOT be enforced anymore.
                    - set to 0 to disable
                */
                "max_players": 100,

                /*
                    Maximum number of caps a team can own while seeding.
                    Player gaining offensive points while their team already owns this number of caps,
                    will be warned/punished.
                    Recommended : 3 (up to the middle point)
                */
                "max_caps": 3,
      
                /*
                    A boolean to indicate if this rule should go straight to punish the player (instead of warn them first).
                    This might be valuable to enable, as the game will only refresh offensive points
                    (which this rule is based upon) every minute.
                    Capping a point takes 2 minutes in warfare mode.
                    A player might get warnings, but the damage capping a point with "just" two warnings
                    might justify directly punishing the player.
                    Recommended : true
                */
                "skip_warning": true,
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
                This automod has 4 steps :
                - 1. internally noting (X times) ;
                - 2. warning via direct message (Y times) ;
                - 3. punish (Z times) ;
                - 4. kick.

                Note :
                The state cycle for a given squad only resets once it finally has more than one member.
                So, for example, if you disabled the kick and have 3 punishes configured,
                once the 3 punishes are through, that's it : nothing will happen anymore for the player,
                even if he's still alone in his armor squad.
            */
            "enabled": false,

            /*
                If this is set to true, NO warning / punish / kick will be applied for real.
                It turns the code into a "simulation" mode
                and only send what it would do to your Discord audit log webhook.
            */
            "dry_run": false,

            /*
                Discord Webhook URL where audit logs should be sent.
            */
            "discord_webhook_url": null,

            /*
                This is either an empty list [], or a list of flags
                to exempt a player from this automod features.
                To use, add a flag or multiple flags to the list,
                then flag the players you want to exempt in the CRCON UI.
            */
            "whitelist_flags": [
                "🚨"
            ],

            /*
                If the player's level is below this number,
                he/she will be immune to punishes and kicks.
                - set to 0 to disable.
            */
            "immune_player_level": 0,

            /*
                If the "enabled" parameter above is set to "true",
                the automod won't do anythying below this number of players on the server.
                - set to 0 if you want the automod to be always active,
                regardless the number of players.
            */
            "dont_do_anything_below_this_number_of_players": 0,

            /*
                Step 1 of 4
                If a player is solo in an armor squad, he will be noted internally but no action will be taken,
                since we sometimes receive wrong data from the game server.
                So we 'note' those players and see if they are still are solo the next time we check.
                - set to 0 to disable (this means it will move to warn directly) ;
                - set to 1 to X to note the squad X times before moving to the warn step ;
                Recommended : 0 (the squad opener will immediatly get the warning).
            */
            "number_of_notes": 0,

            /*
                This is the number of seconds to wait until moving to the next note
                (or to the warning step if 'number_of_notes' is reached).
                Recommended : 10
            */
            "notes_interval_seconds": 10,

            /*
                Step 2 of 4
                Send a direct warning message to the solo tank player.
                - set to 0 to disable (directly move to punish step) ;
                - set to -1 for infinite warnings (will never go to punish step) ;
                - set to 1 or Y to warn squad Y times before moving to punish step.
                Recommended : 2
            */
            "number_of_warnings": 2,

            /*
                This is the number of seconds to wait until moving to the next warning step
                (or to the punish step if 'number_of_warnings' is reached).
            */
            "warning_interval_seconds": 60,

            /*
                The following variables are available :
                - {player_name} ;
                - {squad_name} ;
                - {received_warnings} ;
                - {max_warnings} ;
                - {next_check_seconds}.
            */
            "warning_message": "Warning, {player_name} !\\n\\nYou can't play solo tank on this server !\\n\\nYou will be punished after {max_warnings} warnings\\n(you already received {received_warnings})\\n\\nNext check will happen automatically in {next_check_seconds}s.",

            /*
                Step 3 of 4
                If the player is still solo in his tank
                after 'number_of_warnings' * 'warning_interval_seconds'
                - set to 0 to disable to punish entirely ;
                - set to -1 for infinite punish (will never go to kick step) ;
                - set to Z to apply Z punishes before moving to kick step.
                Recommended : 2
                Advice : set 'number_of_warnings' to -1 if you set this to 0.
            */
            "number_of_punishments": 2,

            /*
                This option is the same as above, but for the entire server.
                If the server has less players than the number you set below,
                no punishes / kicks will be applied.
            */
            "min_server_players_for_punish": 0,

            /*
                This is the number of seconds to wait between punishes.
                Recommended : 60
            */
            "punish_interval_seconds": 60,

            /*
                The following variables are available :
                - {player_name} ;
                - {squad_name} ;
                - {received_punishes} ;
                - {max_punishes} ;
                - {next_check_seconds}.
            */
            "punish_message": "\\n\\nYou've been punished by a bot,\\nbecause you're playing solo in the armor squad {squad_name}.\\n\\n(Punition {received_punishes} of {max_punishes} before kick)\\n\\nNext check in {next_check_seconds}s.\\n\\n",

            /*
                Step 4 of 4
                Note :
                If you have set 'number_of_punishments' to -1 or 0,
                it will never reach that step.
                - set to 'false' if you don't want to kick players after they reached 'number_of_punishments'.
                Advice : set 'number_of_punishments' to -1 if you set this to 'false'.
            */
            "kick_after_max_punish": true,

            /*
                Same behavior as for the punishes :
                kick step is disabled if the server has less players than this.
            */
            "min_server_players_for_kick": 0,

            /*
                Number of seconds to wait before kicking,
                after 'number_of_punishments' has been reached
            */
            "kick_grace_period_seconds": 60,

            /*
                The following variables are available :
                - {player_name} ;
                - {squad_name} ;
                - {kick_grace_period}.
            */
            "kick_message": "You've been kicked by a bot.\\n\\nYou were still playing solo in the armor squad {squad_name},\\n{kick_grace_period}s after being punished."
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
