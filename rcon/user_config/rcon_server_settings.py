from typing import Optional, Type, TypedDict

from pydantic import BaseModel, BeforeValidator, Field, HttpUrl, field_serializer
from typing_extensions import Annotated

from rcon.types import RconInvalidNameActionType, WindowsStoreIdActionType
from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config
from rcon.utils import get_server_number

WHITESPACE_NAME_PLAYER_MESSAGE = """Your name ends in whitespace (or has whitespace in the 20th character)

Because of a bug in the game admin tools this server uses will not work properly,
you might suffer auto-moderation actions as a false-positive.

Please change your name in Steam and restart your game to avoid this.

Please ask T17 to prioritize fixing this bug."""

PINEAPPLE_NAME_PLAYER_MESSAGE = """Your name has a special character around the 20th character (because it is truncated as it is too long)

Because of a bug in the game, admin tools this server uses will not work properly.

Please change your name in Steam and restart your game to avoid this.

Please ask T17 to prioritize fixing this bug."""


INVALID_NAME_AUDIT_MESSAGE = """Player with an invalid name (ends in whitespace or a partial character when truncated) joined: {name} ({player_id}
This will cause errors with various auto mods (no leader, etc) and the `playerinfo` RCON command will not work.
The player will show as 'unassigned' in Gameview.
Action taken = {action}"""
PINEAPPLE_NAMES_AUDIT_UNBAN_MESSAGE = "Unbanning {name} ({player_id}) that was temp banned since the `kick` command will not work with their name"

WINDOWS_STORE_PLAYER_MESSAGE = "Windows store players are not allowed on this server."

WINDOWS_STORE_AUDIT_MESSAGE = (
    "Windows store player {name} ({player_id} connected, action taken = {action})"
)


class InvalidNameType(TypedDict):
    enabled: bool
    action: RconInvalidNameActionType
    whitespace_name_player_message: str
    pineapple_name_player_message: str
    audit_message: str
    # TODO: maybe they'll fix kicking pineapple names one day lol
    audit_kick_unban_message: str
    audit_message_author: str
    ban_length_hours: int


class WindowsStorePlayersType(TypedDict):
    enabled: bool
    action: WindowsStoreIdActionType
    player_message: str
    audit_message: str
    audit_message_author: str
    temp_ban_length_hours: int


class RconServerSettingsType(TypedDict):
    short_name: str
    server_url: HttpUrl
    discord_invite_url: HttpUrl
    lock_stats_api: bool
    # unban_does_unblacklist: bool
    # unblacklist_does_unban: bool
    # broadcast_temp_bans: bool
    broadcast_unbans: bool
    lock_stats_api: bool
    live_stats_refresh_seconds: int
    live_stats_refresh_current_game_seconds: int
    invalid_names: InvalidNameType
    windows_store_players: WindowsStorePlayersType


def _upper_case_action(
    v: str | None, cls: Type[RconInvalidNameActionType | WindowsStoreIdActionType]
):
    if v:
        return cls(v.upper())
    else:
        return v


def upper_case_name_kick_action(v: str | None):
    """Allow users to enter actions in any case"""
    return _upper_case_action(v, cls=RconInvalidNameActionType)


def upper_case_name_windows_player_action(v: str | None):
    """Allow users to enter actions in any case"""
    return _upper_case_action(v, cls=WindowsStoreIdActionType)


class InvalidName(BaseModel):
    enabled: bool = Field(default=False)
    action: (
        Annotated[
            RconInvalidNameActionType, BeforeValidator(upper_case_name_kick_action)
        ]
        | None
    ) = Field(default=None)
    whitespace_name_player_message: str = Field(default=WHITESPACE_NAME_PLAYER_MESSAGE)
    pineapple_name_player_message: str = Field(default=PINEAPPLE_NAME_PLAYER_MESSAGE)
    audit_message: str = Field(default=INVALID_NAME_AUDIT_MESSAGE)
    audit_kick_unban_message: str = Field(default=PINEAPPLE_NAMES_AUDIT_UNBAN_MESSAGE)
    audit_message_author: str = Field(default="CRCON")
    ban_length_hours: int = Field(default=1)


class WindowsStorePlayer(BaseModel):
    enabled: bool = Field(default=False)
    action: (
        Annotated[
            WindowsStoreIdActionType,
            BeforeValidator(upper_case_name_windows_player_action),
        ]
        | None
    ) = Field(default=None)
    player_message: str = Field(default=WINDOWS_STORE_PLAYER_MESSAGE)
    audit_message: str = Field(default=WINDOWS_STORE_AUDIT_MESSAGE)
    audit_message_author: str = Field(default="CRCON")
    temp_ban_length_hours: int = Field(default=1)


class RconServerSettingsUserConfig(BaseUserConfig):
    # Use a callable to defer calling get_server_number until it's used and not on import
    short_name: str = Field(default_factory=lambda: f"MyServer{get_server_number()}")
    server_url: Optional[HttpUrl] = Field(default=None)
    discord_invite_url: Optional[HttpUrl] = Field(default=None)

    lock_stats_api: bool = Field(default=False)
    # unban_does_unblacklist: bool = Field(default=True)
    # unblacklist_does_unban: bool = Field(default=True)
    # broadcast_temp_bans: bool = Field(default=True)
    broadcast_unbans: bool = Field(default=False)

    lock_stats_api: bool = Field(default=False)
    live_stats_refresh_seconds: int = Field(default=15)
    live_stats_refresh_current_game_seconds: int = Field(default=5)

    invalid_names: InvalidName = Field(default_factory=InvalidName)
    windows_store_players: WindowsStorePlayer = Field(
        default_factory=WindowsStorePlayer
    )

    @field_serializer("server_url", "discord_invite_url")
    def serialize_urls(self, url: HttpUrl, _info):
        if url is not None:
            return str(url)
        else:
            return None

    @staticmethod
    def save_to_db(values: RconServerSettingsType, dry_run=False):
        key_check(RconServerSettingsType.__required_keys__, values.keys())

        raw_invalid_names = values.get("invalid_names")
        validated_invalid_names = InvalidName(
            enabled=raw_invalid_names.get("enabled"),
            action=raw_invalid_names.get("action"),
            whitespace_name_player_message=raw_invalid_names.get(
                "whitespace_name_player_message"
            ),
            pineapple_name_player_message=raw_invalid_names.get(
                "pineapple_name_player_message"
            ),
            audit_message=raw_invalid_names.get("audit_message"),
            audit_kick_unban_message=raw_invalid_names.get("audit_kick_unban_message"),
            audit_message_author=raw_invalid_names.get("audit_message_author"),
            ban_length_hours=raw_invalid_names.get("ban_length_hours"),
        )
        raw_win_store_players = values.get("windows_store_players")
        validated_win_store_players = WindowsStorePlayer(
            enabled=raw_win_store_players.get("enabled"),
            action=raw_win_store_players.get("action"),
            player_message=raw_win_store_players.get("player_message"),
            audit_message=raw_win_store_players.get("audit_message"),
            audit_message_author=raw_win_store_players.get("audit_message_author"),
            temp_ban_length_hours=raw_win_store_players.get("temp_ban_length_hours"),
        )

        validated_conf = RconServerSettingsUserConfig(
            short_name=values.get("short_name"),
            server_url=values.get("server_url"),
            discord_invite_url=values.get("discord_invite_url"),
            lock_stats_api=values.get("lock_stats_api"),
            # unban_does_unblacklist=values.get("unban_does_unblacklist"),
            # unblacklist_does_unban=values.get("unblacklist_does_unban"),
            # broadcast_temp_bans=values.get("broadcast_temp_bans"),
            broadcast_unbans=values.get("broadcast_unbans"),
            live_stats_refresh_seconds=values.get("live_stats_refresh_seconds"),
            live_stats_refresh_current_game_seconds=values.get(
                "live_stats_refresh_current_game_seconds"
            ),
            invalid_names=validated_invalid_names,
            windows_store_players=validated_win_store_players,
        )

        if not dry_run:
            set_user_config(RconServerSettingsUserConfig.KEY(), validated_conf)
