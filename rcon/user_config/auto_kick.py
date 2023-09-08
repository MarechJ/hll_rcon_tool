from typing import ClassVar, TypedDict

from pydantic import Field, field_validator

from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config


class AutoVoteKickType(TypedDict):
    minimum_ingame_mods: int
    minimum_online_mods: int
    enabled: bool
    condition: str


VALID_CONDITIONS = ("AND", "OR")


class AutoVoteKickUserConfig(BaseUserConfig):
    KEY_NAME: ClassVar = "auto_votekick_config"

    enabled: bool = Field(default=False, strict=True)
    minimum_ingame_mods: int = Field(ge=0, default=1)
    minimum_online_mods: int = Field(ge=0, default=2)
    condition: str = Field(default="OR")

    @field_validator("condition")
    @classmethod
    def validate_condition(cls, v: str):
        if v.upper() not in VALID_CONDITIONS:
            raise ValueError(f"{v} must be one of {VALID_CONDITIONS}")

        return v

    @staticmethod
    def save_to_db(values: AutoVoteKickType, dry_run=False):
        key_check(AutoVoteKickType.__required_keys__, values.keys())

        validated_conf = AutoVoteKickUserConfig(
            enabled=values.get("enabled"),
            minimum_ingame_mods=values.get("minimum_ingame_mods"),
            minimum_online_mods=values.get("minimum_online_mods"),
            condition=values.get("condition"),
        )

        if not dry_run:
            set_user_config(AutoVoteKickUserConfig.KEY(), validated_conf.model_dump())
