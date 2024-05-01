from typing import TypedDict

from pydantic import Field

from rcon.user_config.utils import BaseUserConfig, set_user_config


class RealVipConfigType(TypedDict):
    enabled: bool
    desired_total_number_vips: int
    minimum_number_vip_slots: int


class RealVipUserConfig(BaseUserConfig):
    enabled: bool = Field(default=False)
    desired_total_number_vips: int = Field(ge=0, default=5)
    minimum_number_vip_slots: int = Field(ge=0, default=1)

    @staticmethod
    def save_to_db(values: RealVipConfigType, dry_run=False):
        validated_conf = RealVipUserConfig(
            enabled=values.get("enabled"),
            desired_total_number_vips=values.get("desired_total_number_vips"),
            minimum_number_vip_slots=values.get("minimum_number_vip_slots"),
        )

        if not dry_run:
            set_user_config(validated_conf.KEY(), validated_conf)
