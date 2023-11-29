from typing import TypedDict

from pydantic import Field

from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config

HELP_TRIGGER = "!help"
VIP_TRIGGER = "!vip"
WHOKILLED_TRIGGER = "!killer"


class TriggerWordsType(TypedDict):
    enabled: bool
    help_trigger: str
    vip_trigger: str
    whokilled_trigger: str
    custom_triggers: dict[str, str]

class TriggerWordsUserConfig(BaseUserConfig):
    enabled: bool = Field(default=False)
    help_trigger: str = Field(default=HELP_TRIGGER)
    vip_trigger: str = Field(default=VIP_TRIGGER)
    whokilled_trigger: str = Field(default=WHOKILLED_TRIGGER)
    custom_triggers: dict[str, str] = Field(default_factory=dict)

    @staticmethod
    def save_to_db(values: TriggerWordsType, dry_run=False) -> None:
        key_check(TriggerWordsType.__required_keys__, values.keys())

        validated_conf = TriggerWordsUserConfig(
            enabled=values.get("enabled"),
            help_trigger=values.get("help_trigger"),
            vip_trigger=values.get("vip_trigger"),
            custom_trigger=values.get("custom_triggers"),
        )

        if not dry_run:
            set_user_config(
                TriggerWordsUserConfig.KEY(), validated_conf.model_dump()
            )
