from typing import TypedDict

from pydantic import Field, field_validator

from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config


class AutoVoteKickType(TypedDict):
    minimum_ingame_mods: int
    minimum_online_mods: int
    enabled: bool
    condition: str


VALID_CONDITIONS = ("AND", "OR")


class AutoVoteKickUserConfig(BaseUserConfig):
    enabled: bool = Field(default=False, strict=True, title="Enable",
                          description="Enable vote kick status by conditions")
    minimum_ingame_mods: int = Field(ge=0, default=1, title="Minimum In-Game Moderators",
                                     description="The number of moderators (Player IDs must be set in the admin site) in game for vote kick to be automatically turned off")
    minimum_online_mods: int = Field(ge=0, default=2, title="Minimum Online Moderators",
                                     description="The number of moderators (steam IDs must be set in the admin site) with CRCON open for vote kick to be automatically turned off")
    condition: str = Field(default="OR", title="Condition",
                           description="AND or OR for Minimum In-Game Moderators/Minimum Online Moderators criteria")

    @field_validator("condition")
    @classmethod
    def validate_condition(cls, v: str):
        if v.upper() not in VALID_CONDITIONS:
            raise ValueError(f"{v} must be one of {VALID_CONDITIONS}")

        return v

    @staticmethod
    def save_to_db(values: AutoVoteKickType, dry_run=False):
        key_check(
            AutoVoteKickType.__required_keys__,
            AutoVoteKickType.__optional_keys__,
            values.keys(),
        )

        validated_conf = AutoVoteKickUserConfig(
            enabled=values.get("enabled"),
            minimum_ingame_mods=values.get("minimum_ingame_mods"),
            minimum_online_mods=values.get("minimum_online_mods"),
            condition=values.get("condition"),
        )

        if not dry_run:
            set_user_config(AutoVoteKickUserConfig.KEY(), validated_conf)
