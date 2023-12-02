from typing import TypedDict

from pydantic import Field

from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config

SEED_TIME_TEXT = "Welcome !\nThe server is seeding\n\nPlease respect the special rules !"
NON_SEED_TIME_TEXT = "Welcome !\nThe server is NOT in seed !"


class MessageOnConnectType(TypedDict):
    enabled: bool
    seed_limit: int
    seed_time_text: str
    non_seed_time_text: str


class MessageOnConnectUserConfig(BaseUserConfig):
    """
    Args:
        enabled bool:
            Enable message at player's connection
        seed_limit int:
            The number of players in game to stop the seeding time
        seed_time_text str:
            A message that will be sent to any entering player in seed time
        non_seed_time_text str:
            A message that will be sent to any entering player in non-seed time
    """

    enabled: bool = Field(default=False, strict=True)
    seed_limit: int = Field(ge=0, le=100, default=40)
    seed_time_text: str = Field(default=SEED_TIME_TEXT)
    non_seed_time_text: str = Field(default=NON_SEED_TIME_TEXT)

    @staticmethod
    def save_to_db(values: MessageOnConnectType, dry_run=False):
        key_check(MessageOnConnectType.__required_keys__, values.keys())

        validated_conf = MessageOnConnectUserConfig(
            enabled=values.get("enabled"),
            seed_limit=values.get("seed_limit"),
            seed_time_text=values.get("seed_time_text"),
            non_seed_time_text=values.get("non_seed_time_text"),
        )

        if not dry_run:
            set_user_config(MessageOnConnectUserConfig.KEY(), validated_conf.model_dump())
