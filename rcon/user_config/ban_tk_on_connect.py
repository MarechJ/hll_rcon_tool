from typing import Optional, TypedDict

from pydantic import BaseModel, Field, HttpUrl, field_serializer

from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config

DISCORD_WEBHOOK_MESSAGE = "{player} banned for TK right after connecting"
MESSAGE = "Your first action on the server was a TEAM KILL you were banned as a result"


class BanTeamKillOnConnectWhitelistType(TypedDict):
    has_flag: list[str]
    is_vip: bool
    has_at_least_n_sessions: int


class BanTeamKillOnConnectType(TypedDict):
    enabled: bool
    message: str
    author_name: str
    blacklist_id: int | None
    excluded_weapons: list[str]
    max_time_after_connect_minutes: int
    ignore_tk_after_n_kills: int
    ignore_tk_after_n_deaths: int
    whitelist_players: BanTeamKillOnConnectWhitelistType
    teamkill_tolerance_count: int
    discord_webhook_url: Optional[HttpUrl]
    discord_webhook_message: str


class BanTeamKillOnConnectWhiteList(BaseModel):
    has_flag: list[str] = Field(default_factory=list)
    is_vip: bool = Field(default=True)
    has_at_least_n_sessions: int = Field(ge=0, default=10)


class BanTeamKillOnConnectUserConfig(BaseUserConfig):
    enabled: bool = Field(default=False)
    message: str = Field(default=MESSAGE)
    author_name: str = Field(default="HATERS GONNA HATE")
    blacklist_id: int | None = None
    excluded_weapons: list[str] = Field(default_factory=list)
    max_time_after_connect_minutes: int = Field(ge=1, default=5)
    ignore_tk_after_n_kills: int = Field(ge=1, default=1)
    ignore_tk_after_n_deaths: int = Field(ge=1, default=2)
    whitelist_players: BanTeamKillOnConnectWhiteList = Field(
        default_factory=BanTeamKillOnConnectWhiteList
    )
    teamkill_tolerance_count: int = Field(ge=0, default=1)
    discord_webhook_url: Optional[HttpUrl] = Field(default=None)
    discord_webhook_message: str = Field(default=DISCORD_WEBHOOK_MESSAGE)

    @field_serializer("discord_webhook_url")
    def serialize_server_url(self, discord_webhook_url: HttpUrl, _info):
        if discord_webhook_url is not None:
            return str(discord_webhook_url)
        else:
            return None

    @staticmethod
    def save_to_db(values: BanTeamKillOnConnectType, dry_run=False):
        key_check(BanTeamKillOnConnectType.__required_keys__, BanTeamKillOnConnectType.__optional_keys__, values.keys())

        whitelist_players = BanTeamKillOnConnectWhiteList(
            has_flag=values.get("whitelist_players", {}).get("has_flag"),
            is_vip=values.get("whitelist_players", {}).get("is_vip"),
            has_at_least_n_sessions=values.get("whitelist_players", {}).get(
                "has_at_least_n_sessions"
            ),
        )

        validated_conf = BanTeamKillOnConnectUserConfig(
            enabled=values.get("enabled"),
            message=values.get("message"),
            blacklist_id=values.get("blacklist_id"),
            author_name=values.get("author_name"),
            excluded_weapons=values.get("excluded_weapons"),
            max_time_after_connect_minutes=values.get("max_time_after_connect_minutes"),
            ignore_tk_after_n_kills=values.get("ignore_tk_after_n_kills"),
            ignore_tk_after_n_deaths=values.get("ignore_tk_after_n_deaths"),
            whitelist_players=whitelist_players,
            teamkill_tolerance_count=values.get("teamkill_tolerance_count"),
            discord_webhook_url=values.get("discord_webhook_url"),
            discord_webhook_message=values.get("discord_webhook_message"),
        )

        if not dry_run:
            set_user_config(BanTeamKillOnConnectUserConfig.KEY(), validated_conf)
