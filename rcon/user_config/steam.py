from typing import TypedDict

from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config


class SteamType(TypedDict):
    api_key: str | None


class SteamUserConfig(BaseUserConfig):
    NAME = "SteamUserConfig"

    api_key: str | None = None

    @staticmethod
    def save_to_db(values: SteamType, dry_run=False):
        key_check(
            SteamType.__required_keys__, SteamType.__optional_keys__, values.keys()
        )

        validated_conf = SteamUserConfig(api_key=values.get("api_key"))

        if not dry_run:
            set_user_config(SteamUserConfig.NAME, validated_conf)
