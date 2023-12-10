from typing import Optional, TypedDict

from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config


class SteamType(TypedDict):
    api_key: str | None


class SteamUserConfig(BaseUserConfig):
    api_key: Optional[str] = None

    @staticmethod
    def save_to_db(values: SteamType, dry_run=False):
        key_check(SteamType.__required_keys__, values.keys())

        validated_conf = SteamUserConfig(api_key=values.get("api_key"))

        if not dry_run:
            set_user_config(SteamUserConfig.KEY(), validated_conf.model_dump())
