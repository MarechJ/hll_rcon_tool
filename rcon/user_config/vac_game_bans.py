from typing import TypedDict

from pydantic import Field

from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config

BAN_ON_VAC_HISTORY_REASON = "VAC/Game ban history ({DAYS_SINCE_LAST_BAN} days ago)"


class VacGameBansType(TypedDict):
    vac_history_days: int
    game_ban_threshhold: int
    ban_on_vac_history_reason: str
    whitelist_flags: list[str]


class VacGameBansUserConfig(BaseUserConfig):
    vac_history_days: int = Field(ge=0, default=0)
    game_ban_threshhold: int = Field(ge=0, default=0)
    blacklist_id: int | None = None
    ban_on_vac_history_reason: str = Field(default=BAN_ON_VAC_HISTORY_REASON)
    auto_expire: bool = False
    whitelist_flags: list[str] = Field(default_factory=list)

    @staticmethod
    def save_to_db(values: VacGameBansType, dry_run=False):
        key_check(VacGameBansType.__required_keys__, values.keys())

        validated_conf = VacGameBansUserConfig(
            vac_history_days=values.get("vac_history_days"),
            game_ban_threshhold=values.get("game_ban_threshhold"),
            blacklist_id=values.get("blacklist_id"),
            ban_on_vac_history_reason=values.get("ban_on_vac_history_reason"),
            auto_expire=values.get("auto_expire", False),
            whitelist_flags=values.get("whitelist_flags"),
        )

        if not dry_run:
            set_user_config(VacGameBansUserConfig.KEY(), validated_conf)
