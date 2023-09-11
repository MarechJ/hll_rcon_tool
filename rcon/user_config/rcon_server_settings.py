from typing import ClassVar, TypedDict

from pydantic import Field

from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config


class RconServerSettingsType(TypedDict):
    lock_stats_api: bool
    unban_does_unblacklist: bool
    unblacklist_does_unban: bool
    broadcast_temp_bans: bool
    broadcast_unbans: bool


class RconServerSettingsUserConfig(BaseUserConfig):
    KEY_NAME: ClassVar = "steam_settings"

    lock_stats_api: bool = Field(default=False)
    unban_does_unblacklist: bool = Field(default=True)
    # TODO: this isn't actually used anywhere
    unblacklist_does_unban: bool = Field(default=True)
    broadcast_temp_bans: bool = Field(default=True)
    broadcast_unbans: bool = Field(default=True)

    @staticmethod
    def save_to_db(values: RconServerSettingsType, dry_run=False):
        key_check(RconServerSettingsType.__required_keys__, values.keys())

        validated_conf = RconServerSettingsUserConfig(
            lock_stats_api=values.get("lock_stats_api"),
            unban_does_unblacklist=values.get("unban_does_unblacklist"),
            unblacklist_does_unban=values.get("unblacklist_does_unban"),
            broadcast_temp_bans=values.get("broadcast_temp_bans"),
            broadcast_unbans=values.get("broadcast_unbans"),
        )

        if not dry_run:
            set_user_config(
                RconServerSettingsUserConfig.KEY(), validated_conf.model_dump()
            )
