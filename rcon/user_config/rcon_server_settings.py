from typing import ClassVar, TypedDict

from pydantic import Field

from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config
from rcon.utils import get_server_number


class RconServerSettingsType(TypedDict):
    short_name: str
    lock_stats_api: bool
    unban_does_unblacklist: bool
    unblacklist_does_unban: bool
    broadcast_temp_bans: bool
    broadcast_unbans: bool
    lock_stats_api: bool
    live_stats_refresh_seconds: int
    live_stats_refresh_current_game_seconds: int


class RconServerSettingsUserConfig(BaseUserConfig):
    KEY_NAME: ClassVar = "steam_settings"

    short_name: str = Field(default=f"MyServer{get_server_number()}")
    lock_stats_api: bool = Field(default=False)
    unban_does_unblacklist: bool = Field(default=True)
    # TODO: this isn't actually used anywhere
    unblacklist_does_unban: bool = Field(default=True)
    broadcast_temp_bans: bool = Field(default=True)
    broadcast_unbans: bool = Field(default=True)

    lock_stats_api: bool = Field(default=False)
    live_stats_refresh_seconds: int = Field(default=15)
    live_stats_refresh_current_game_seconds: int = Field(default=5)

    @staticmethod
    def save_to_db(values: RconServerSettingsType, dry_run=False):
        key_check(RconServerSettingsType.__required_keys__, values.keys())

        validated_conf = RconServerSettingsUserConfig(
            lock_stats_api=values.get("lock_stats_api"),
            unban_does_unblacklist=values.get("unban_does_unblacklist"),
            unblacklist_does_unban=values.get("unblacklist_does_unban"),
            broadcast_temp_bans=values.get("broadcast_temp_bans"),
            broadcast_unbans=values.get("broadcast_unbans"),
            live_stats_refresh_seconds=values.get("live_stats_refresh_seconds"),
            live_stats_refresh_current_game_seconds=values.get(
                "live_stats_refresh_current_game_seconds"
            ),
        )

        if not dry_run:
            set_user_config(
                RconServerSettingsUserConfig.KEY(), validated_conf.model_dump()
            )
