from typing import Optional, TypedDict

from pydantic import Field, IPvAnyAddress, field_validator

from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config


class GtxServerNameChangeType(TypedDict):
    ip: str
    port: int
    username: str
    password: str


class GtxServerNameChangeUserConfig(BaseUserConfig):
    ip: str = Field(default="127.0.0.1")
    port: int = Field(default=0)
    username: Optional[str] = Field(default=None)
    password: Optional[str] = Field(default=None)

    @field_validator("ip")
    @classmethod
    def validate_ip_addr_format(cls, v):
        # Store as a string, but make sure that it validates
        # as an IP address
        IPvAnyAddress(v)
        return v

    @staticmethod
    def save_to_db(values: GtxServerNameChangeType, dry_run=False):
        key_check(GtxServerNameChangeType.__required_keys__, values.keys())

        validated_conf = GtxServerNameChangeUserConfig(
            ip=values.get("ip"),
            port=values.get("port"),
            username=values.get("username"),
            password=values.get("password"),
        )

        if not dry_run:
            set_user_config(
                GtxServerNameChangeUserConfig.KEY(), validated_conf.model_dump()
            )
