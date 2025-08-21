from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Literal, ParamSpec, TypeVar

from pydantic import BaseModel

from hllrcon.data import layers
from hllrcon.exceptions import HLLCommandError, HLLMessageError
from hllrcon.responses import (
    GetAdminLogResponse,
    GetBannedWordsResponse,
    GetCommandDetailsResponse,
    GetCommandsResponse,
    GetMapRotationResponse,
    GetPlayerResponse,
    GetPlayersResponse,
    GetServerConfigResponse,
    GetServerSessionResponse,
)

P = ParamSpec("P")
ModelT = TypeVar("ModelT", bound=BaseModel)

GameMode = Literal["Warfare", "Offensive", "Skirmish"]


def cast_response_to_model(
    model_type: type[ModelT],
):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs) -> ModelT:
            result = func(*args, **kwargs)
            return model_type.model_validate_json(result)

        return wrapper

    return decorator


def cast_response_to_bool(
    status_codes: set[int],
):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs) -> bool:
            try:
                func(*args, **kwargs)
            except HLLCommandError as e:
                if e.status_code in status_codes:
                    return False
                raise
            return True

        return wrapper

    return decorator


class RconCommands(ABC):
    @abstractmethod
    def execute(
        self,
        command: str,
        version: int,
        body: str | dict[str, Any] = "",
    ) -> str:
        """Execute a command on the RCON server.

        Parameters
        ----------
        command : str
            The command to execute.
        version : int
            The version of the command to execute.
        body : str | dict[str, Any], optional
            The body of the command, by default an empty string.

        Returns
        -------
        str
            The response from the server.

        """

    def add_admin(self, player_id: str, admin_group: str, comment: str) -> None:
        """Add a player to an admin group.

        Groups are defined in the server's configuration file. The group determines
        whether the player is able to enter admin camera and kick or ban players.

        Parameters
        ----------
        player_id : str
            The ID of the player to add as an admin.
        admin_group : str
            The group to add the player to.
        comment : str
            A comment to identify the admin. This is usually the name of the player.

        """
        self.execute(
            "AddAdmin",
            2,
            {"PlayerId": player_id, "AdminGroup": admin_group, "Comment": comment},
        )

    def remove_admin(self, player_id: str) -> None:
        """Remove a player from their admin group.

        Parameters
        ----------
        player_id : str
            The ID of the player to remove as an admin.

        """
        self.execute(
            "RemoveAdmin",
            2,
            {
                "PlayerId": player_id,
            },
        )

    @cast_response_to_model(GetAdminLogResponse)
    def get_admin_log(self, seconds_span: int, filter_: str | None = None) -> str:
        """Retrieve admin logs from the server.

        Parameters
        ----------
        seconds_span : int
            The number of seconds to look back in the logs.
        filter_ : str | None
            A filter string to apply to the logs, by default None.

        """
        if seconds_span < 0:
            msg = "seconds_span must be a non-negative integer"
            raise ValueError(msg)

        return self.execute(
            "GetAdminLog",
            2,
            {
                "LogBackTrackTime": seconds_span,
                "Filters": filter_ or "",
            },
        )

    def change_map(self, map_name: str | layers.Layer) -> None:
        """Change the current map to the specified map.

        Map changes are not immediate. Instead, a 60 second countdown is started.

        Parameters
        ----------
        map_name : str | Layer
            The name of the map to change to.

        """
        self.execute(
            "ChangeMap",
            2,
            {
                "MapName": str(map_name),
            },
        )

    def get_available_sector_names(
        self,
    ) -> tuple[list[str], list[str], list[str], list[str], list[str]]:
        """Retrieve a list of all sector names available on the current map.

        Returns
        -------
        tuple[list[str], list[str], list[str], list[str], list[str]]
            A list of sector names available on the current map.

        """
        details = self.get_command_details("SetSectorLayout")
        parameters = details.dialogue_parameters
        if not parameters or not all(
            p.id.startswith("Sector_") for p in parameters[:5]
        ):
            msg = "Received unexpected response from server."
            raise HLLMessageError(msg)
        return (
            parameters[0].value_member.split(","),
            parameters[1].value_member.split(","),
            parameters[2].value_member.split(","),
            parameters[3].value_member.split(","),
            parameters[4].value_member.split(","),
        )

    def set_sector_layout(
        self,
        sector1: str,
        sector2: str,
        sector3: str,
        sector4: str,
        sector5: str,
    ) -> None:
        """Immediately restart the map with the given sector layout.

        Parameters
        ----------
        sector1 : str
            The name of the first sector.
        sector2 : str
            The name of the second sector.
        sector3 : str
            The name of the third sector.
        sector4 : str
            The name of the fourth sector.
        sector5 : str
            The name of the fifth sector.

        """
        self.execute(
            "SetSectorLayout",
            2,
            {
                "Sector_1": sector1,
                "Sector_2": sector2,
                "Sector_3": sector3,
                "Sector_4": sector4,
                "Sector_5": sector5,
            },
        )

    def add_map_to_rotation(
        self,
        map_name: str | layers.Layer,
        index: int,
    ) -> None:
        """Add a map to the map rotation.

        Parameters
        ----------
        map_name : str | Layer
            The name of the map to add.
        index : int
            The index in the rotation to add the map at.

        """
        self.execute(
            "AddMapToRotation",
            2,
            {
                "MapName": str(map_name),
                "Index": index,
            },
        )

    def remove_map_from_rotation(self, index: int) -> None:
        """Remove a map from the map rotation.

        Parameters
        ----------
        index : int
            The index of the map to remove from the rotation.

        """
        self.execute(
            "RemoveMapFromRotation",
            2,
            {
                "Index": index,
            },
        )

    def add_map_to_sequence(
        self,
        map_name: str | layers.Layer,
        index: int,
    ) -> None:
        """Add a map to the map sequence.

        Parameters
        ----------
        map_name : str | Layer
            The name of the map to add.
        index : int
            The index in the sequence to add the map at.

        """
        self.execute(
            "AddMapToSequence",
            2,
            {
                "MapName": str(map_name),
                "Index": index,
            },
        )

    def remove_map_from_sequence(self, index: int) -> None:
        """Remove a map from the map sequence.

        Parameters
        ----------
        index : int
            The index of the map to remove from the sequence.

        """
        self.execute(
            "RemoveMapFromSequence",
            2,
            {
                "Index": index,
            },
        )

    def set_map_shuffle_enabled(self, *, enabled: bool) -> None:
        """Enable or disable map shuffling of the map sequence.

        Parameters
        ----------
        enabled : bool
            Whether to enable or disable map shuffling.

        """
        self.execute(
            "SetShuffleMapSequence",
            2,
            {
                "Enable": enabled,
            },
        )

    def move_map_in_sequence(self, old_index: int, new_index: int) -> None:
        """Move a map in the map sequence.

        Parameters
        ----------
        old_index : int
            The current index of the map in the sequence.
        new_index : int
            The new index to move the map to in the sequence.

        """
        self.execute(
            "MoveMapInSequence",
            2,
            {
                "CurrentIndex": old_index,
                "NewIndex": new_index,
            },
        )

    def get_available_maps(self) -> list[str]:
        """Retrieve a list of all maps available on the server.

        Returns
        -------
        list[str]
            A list of map names available on the server.

        """
        details = self.get_command_details("AddMapToRotation")
        parameters = details.dialogue_parameters
        if not parameters or parameters[0].id != "MapName":
            msg = "Received unexpected response from server."
            raise HLLMessageError(msg)
        return parameters[0].value_member.split(",")

    @cast_response_to_model(GetCommandsResponse)
    def get_commands(self) -> str:
        """Retrieve a description of all the commands available on the server.

        Returns
        -------
        GetAllCommandsResponse
            A response containing a list of all commands available on the server.

        """
        return self.execute("GetDisplayableCommands", 2)

    def set_team_switch_cooldown(self, minutes: int) -> None:
        """Set the cooldown for switching teams.

        Parameters
        ----------
        minutes : int
            The number of minutes to set the cooldown to. Set to 0 for no cooldown.

        """
        self.execute(
            "SetTeamSwitchCooldown",
            2,
            {
                "TeamSwitchTimer": minutes,
            },
        )

    def set_max_queued_players(self, num: int) -> None:
        """Set the maximum number of players that can be queued for the server.

        Parameters
        ----------
        num : int
            The maximum number of players that can be queued. Must be between 0 and 6.

        """
        self.execute(
            "SetMaxQueuedPlayers",
            2,
            {
                "MaxQueuedPlayers": num,
            },
        )

    def set_idle_kick_duration(self, minutes: int) -> None:
        """Set the number of minutes a player can be idle for before being kicked.

        Parameters
        ----------
        minutes : int
            The number of minutes a player can be idle for before being kicked.
            Set to 0 to disable.

        """
        self.execute(
            "SetIdleKickDuration",
            2,
            {
                "IdleTimeoutMinutes": minutes,
            },
        )

    def set_welcome_message(self, message: str) -> None:
        """Set the welcome message for the server.

        The welcome message is displayed to players on the deployment screen and briefly
        when they first spawn in. The message will be briefly shown again when updated.

        Parameters
        ----------
        message : str
            The welcome message to set.

        """
        self.execute(
            "SendServerMessage",
            2,
            {
                "Message": message,
            },
        )

    @cast_response_to_model(GetPlayerResponse)
    def get_player(self, player_id: str) -> str:
        """Retrieve detailed information about a player currently on the server.

        Parameters
        ----------
        player_id : str
            The ID of the player to retrieve information about.

        Returns
        -------
        GetPlayerResponse
            Information about the player.

        """
        return self.execute(
            "GetServerInformation",
            2,
            {"Name": "player", "Value": player_id},
        )

    @cast_response_to_model(GetPlayersResponse)
    def get_players(self) -> str:
        """Retrieve detailed information about all players currently on the server.

        This is equivalent to calling `get_player` for each player on the server.

        Returns
        -------
        GetPlayersResponse
            Information about all players.

        """
        return self.execute(
            "GetServerInformation",
            2,
            {"Name": "players", "Value": ""},
        )

    @cast_response_to_model(GetMapRotationResponse)
    def get_map_rotation(self) -> str:
        """Retrieve the current map rotation of the server.

        Returns
        -------
        GetMapRotationResponse
            The current map rotation of the server.

        """
        return self.execute(
            "GetServerInformation",
            2,
            {"Name": "maprotation", "Value": ""},
        )

    @cast_response_to_model(GetMapRotationResponse)
    def get_map_sequence(self) -> str:
        """Retrieve the current map sequence of the server.

        Returns
        -------
        GetMapRotationResponse
            The current map sequence of the server.

        """
        return self.execute(
            "GetServerInformation",
            2,
            {"Name": "mapsequence", "Value": ""},
        )

    @cast_response_to_model(GetServerSessionResponse)
    def get_server_session(self) -> str:
        """Retrieve information abou the current server session.

        Returns
        -------
        GetServerSessionResponse
            Information about the current server session.

        """
        return self.execute(
            "GetServerInformation",
            2,
            {"Name": "session", "Value": ""},
        )

    @cast_response_to_model(GetServerConfigResponse)
    def get_server_config(self) -> str:
        """Retrieve the server configuration.

        Returns
        -------
        GetServerConfigResponse
            The server configuration.

        """
        return self.execute(
            "GetServerInformation",
            2,
            {"Name": "serverconfig", "Value": ""},
        )

    @cast_response_to_model(GetBannedWordsResponse)
    def get_banned_words(self) -> str:
        """Retrieve the list of banned words on the server.

        Returns
        -------
        GetBannedWordsResponse
            The list of banned words on the server.

        """
        return self.execute(
            "GetServerInformation",
            2,
            {"Name": "bannedwords", "Value": ""},
        )

    def broadcast(self, message: str) -> None:
        """Broadcast a message to all players on the server.

        Broadcast messages are displayed top-left on the screen for all players.

        Parameters
        ----------
        message : str
            The message to broadcast to all players.

        """
        self.execute(
            "ServerBroadcast",
            2,
            {
                "Message": message,
            },
        )

    def set_high_ping_threshold(self, ms: int) -> None:
        """Set the ping threshold for players.

        If a player's ping exceeds this threshold, they will be kicked from the server.

        Parameters
        ----------
        ms : int
            The ping threshold in milliseconds. Set to 0 to disable.

        """
        self.execute(
            "SetHighPingThreshold",
            2,
            {
                "HighPingThresholdMs": ms,
            },
        )

    @cast_response_to_model(GetCommandDetailsResponse)
    def get_command_details(self, command: str) -> str:
        """Retrieve detailed information about a specific command.

        Parameters
        ----------
        command : str
            The name of the command to retrieve information about.

        Returns
        -------
        GetCommandDetailsResponse
            Information about the command, including its parameters and description.

        """
        return self.execute("GetClientReferenceData", 2, command)

    def message_player(self, player_id: str, message: str) -> None:
        """Send a message to a specific player on the server.

        The message will be displayed in a box in the top right corner of the player's
        screen.

        Parameters
        ----------
        player_id : str
            The ID of the player to send the message to.
        message : str
            The message to send to the player.

        """
        self.execute(
            "MessagePlayer",
            2,
            {
                "Message": message,
                "PlayerId": player_id,
            },
        )

    @cast_response_to_bool({500})
    def kill_player(self, player_id: str, message: str | None = None) -> None:
        """Kill a specific player on the server.

        Parameters
        ----------
        player_id : str
            The ID of the player to kill.
        message : str | None
            The reason for killing the player. This will be displayed to the player, by
            default None.

        Returns
        -------
        bool
            Whether the player was successfully killed. If the player is not on the
            server or already dead, this will return `False`.

        """
        self.execute(
            "PunishPlayer",
            2,
            {
                "PlayerId": player_id,
                "Reason": message,
            },
        )

    @cast_response_to_bool({400})
    def kick_player(self, player_id: str, message: str) -> None:
        """Kick a specific player from the server.

        Parameters
        ----------
        player_id : str
            The ID of the player to kick.
        message : str
            The reason for kicking the player. This will be displayed to the player.

        Returns
        -------
        bool
            Whether the player was successfully kicked. If the player is not on the
            server, this will return `False`.

        """
        self.execute(
            "KickPlayer",
            2,
            {
                "PlayerId": player_id,
                "Reason": message,
            },
        )

    def ban_player(
        self,
        player_id: str,
        reason: str,
        admin_name: str,
        duration_hours: int | None = None,
    ) -> None:
        """Ban a specific player from the server.

        Parameters
        ----------
        player_id : str
            The ID of the player to ban.
        reason : str
            The reason for banning the player. This will be displayed to the player.
        admin_name : str
            The name of the admin performing the ban.
        duration_hours : int | None, optional
            The duration of the ban in hours. If `None`, the player will be permanently
            banned. Defaults to `None`.

        """
        if duration_hours:
            self.execute(
                "TemporaryBanPlayer",
                2,
                {
                    "PlayerId": player_id,
                    "Duration": duration_hours,
                    "Reason": reason,
                    "AdminName": admin_name,
                },
            )
        else:
            self.execute(
                "PermanentBanPlayer",
                2,
                {
                    "PlayerId": player_id,
                    "Reason": reason,
                    "AdminName": admin_name,
                },
            )

    @cast_response_to_bool({400})
    def remove_temporary_ban(self, player_id: str) -> None:
        """Remove a temporary ban for a specific player.

        Parameters
        ----------
        player_id : str
            The ID of the player to remove the temporary ban for.

        Returns
        -------
        bool
            Whether the player was successfully unbanned. If the player is not
            temporarily banned, this will return `False`.

        """
        self.execute(
            "RemoveTemporaryBan",
            2,
            {
                "PlayerId": player_id,
            },
        )

    @cast_response_to_bool({400})
    def remove_permanent_ban(self, player_id: str) -> None:
        """Remove a permanent ban for a specific player.

        Parameters
        ----------
        player_id : str
            The ID of the player to remove the permanent ban for.

        Returns
        -------
        bool
            Whether the player was successfully unbanned. If the player is not
            permanently banned, this will return `False`.

        """
        self.execute(
            "RemovePermanentBan",
            2,
            {
                "PlayerId": player_id,
            },
        )

    def unban_player(self, player_id: str) -> bool:
        """Remove any temporary or permanent ban for a specific player.

        This is equivalent to calling both `remove_temporary_ban` and
        `remove_permanent_ban` for the player.

        Parameters
        ----------
        player_id : str
            The ID of the player to remove the ban for.

        Returns
        -------
        bool
            Whether the player was successfully unbanned. If the player is not
            banned, this will return `False`.

        """
        responses = (
            self.remove_temporary_ban(player_id),
            self.remove_permanent_ban(player_id),
        )
        return any(responses)

    def set_auto_balance_enabled(self, *, enabled: bool) -> None:
        """Enable or disable team balancing.

        When enabled, the server will prevent players from joining a team when
        it has significantly more players than the other team. This treshold is
        configurable with `set_auto_balance_threshold`.

        Parameters
        ----------
        enabled : bool
            Whether to enable or disable auto balancing.

        """
        self.execute(
            "SetAutoBalance",
            2,
            {
                "EnableAutoBalance": enabled,
            },
        )

    def set_auto_balance_threshold(self, player_threshold: int) -> None:
        """Set the player threshold for auto balancing.

        For example, with a threshold of 2, a player is only allowed to join a team if
        after joining it would have at most 2 more players than the other team.

        Setting the threshold to 0 will NOT disable auto balancing! For that purpose,
        use `set_auto_balance_enabled` instead.

        Parameters
        ----------
        player_threshold : int
            The number of players that can be more on one team than the other.
            Must be a non-negative integer.

        """
        self.execute(
            "SetAutoBalanceThreshold",
            2,
            {
                "AutoBalanceThreshold": player_threshold,
            },
        )

    def set_vote_kick_enabled(self, *, enabled: bool) -> None:
        """Enable or disable vote kicking.

        Parameters
        ----------
        enabled : bool
            Whether to enable or disable vote kicking.

        """
        self.execute(
            "SetVoteKick",
            2,
            {
                "Enabled": enabled,
            },
        )

    def reset_vote_kick_thresholds(self) -> None:
        """Reset the vote kick thresholds to the default values."""
        self.execute("ResetKickThreshold", 2)

    def set_vote_kick_thresholds(self, thresholds: list[tuple[int, int]]) -> None:
        """Set the vote kick thresholds for different player counts.

        The thresholds are a list of tuples, where each tuple contains the number of
        players and the number of votes required to kick a player. For example, a
        threshold of (5, 3) means that if there are 5 players on the server, 3 votes
        are required to kick a player.

        Parameters
        ----------
        thresholds : list[tuple[int, int]]
            A list of tuples containing the player count and the number of votes
            required to kick a player.

        """
        self.execute(
            "SetVoteKickThreshold",
            2,
            {
                "ThresholdValue": ",".join([f"{p},{v}" for p, v in thresholds]),
            },
        )

    def add_banned_words(self, words: list[str]) -> None:
        """Add words to the list of banned words on the server.

        Banned works will be replaced with asterisks when sent in chat.

        Parameters
        ----------
        words : list[str]
            A list of words or phrases to add to the list of banned words.

        """
        self.execute(
            "AddBannedWords",
            2,
            {
                "Words": ",".join(words),
            },
        )

    def remove_banned_words(self, words: list[str]) -> None:
        """Remove words from the list of banned words on the server.

        Parameters
        ----------
        words : list[str]
            A list of words or phrases to remove from the list of banned words.

        """
        self.execute(
            "RemoveBannedWords",
            2,
            {
                "Words": ",".join(words),
            },
        )

    def add_vip(self, player_id: str, description: str) -> None:
        """Add a player to the VIP list.

        Parameters
        ----------
        player_id : str
            The ID of the player to add as a VIP.
        description : str
            A description of the VIP. This is usually the name of the player.

        """
        self.execute(
            "AddVip",
            2,
            {
                "PlayerId": player_id,
                "Description": description,
            },
        )

    def remove_vip(self, player_id: str) -> None:
        """Remove a player from the VIP list.

        Parameters
        ----------
        player_id : str
            The ID of the player to remove from the VIP list.

        """
        self.execute(
            "RemoveVip",
            2,
            {
                "PlayerId": player_id,
            },
        )

    def set_match_timer(self, game_mode: GameMode, minutes: int) -> None:
        """Set the match timer for a specific game mode.

        This does not affect the current match, but will apply to all future matches
        of the specified game mode. Limits apply, depending on the game mode.

        Parameters
        ----------
        game_mode : GameMode
            The game mode to set the match timer for. One of "Warfare", "Offensive",
            or "Skirmish".
        minutes : int
            The number of minutes to set the match timer to.

        """
        self.execute(
            "SetMatchTimer",
            2,
            {
                "GameMode": game_mode,
                "MatchLength": minutes,
            },
        )

    def reset_match_timer(self, game_mode: GameMode) -> None:
        """Reset the match timer for a specific game mode.

        This does not affect the current match, but will apply to all future matches
        of the specified game mode. The match timer will be set to the default value.

        Parameters
        ----------
        game_mode : GameMode
            The game mode to reset the match timer for. One of "Warfare", "Offensive",
            or "Skirmish".

        """
        self.execute(
            "RemoveMatchTimer",
            2,
            {
                "GameMode": game_mode,
            },
        )

    def set_warmup_timer(self, game_mode: GameMode, minutes: int) -> None:
        """Set the warmup timer for a specific game mode.

        This does not affect the current match, but will apply to all future matches
        of the specified game mode. Limits apply, depending on the game mode.

        Parameters
        ----------
        game_mode : GameMode
            The game mode to set the warmup timer for. One of "Warfare", "Offensive",
            or "Skirmish".
        minutes : int
            The number of minutes to set the warmup timer to.

        """
        self.execute(
            "SetWarmupTimer",
            2,
            {
                "GameMode": game_mode,
                "WarmupLength": minutes,
            },
        )

    def remove_warmup_timer(self, game_mode: GameMode) -> None:
        """Reset the warmup timer for a specific game mode.

        This does not affect the current match, but will apply to all future matches
        of the specified game mode. The warmup timer will be set to the default value.

        Parameters
        ----------
        game_mode : GameMode
            The game mode to reset the warmup timer for. One of "Warfare", "Offensive",
            or "Skirmish".

        """
        self.execute(
            "RemoveWarmupTimer",
            2,
            {
                "GameMode": game_mode,
            },
        )

    def set_dynamic_weather_enabled(self, map_id: str, *, enabled: bool) -> None:
        """Enable or disable dynamic weather for a specific map.

        Not all maps have dynamic weather. Maps that do not support dynamic weather
        will ignore this command.

        This does not affect the current match, but will apply to all future
        matches on the specified map.

        Parameters
        ----------
        map_id : str
            The ID of the map to enable or disable dynamic weather for.
        enabled : bool
            Whether to enable or disable dynamic weather for the map.

        """
        self.execute(
            "SetMapWeatherToggle",
            2,
            {
                "MapId": map_id,
                "Enable": enabled,
            },
        )
