from typing import ClassVar, Optional, TypedDict

from pydantic import Field, IPvAnyAddress, field_validator

from rcon.user_config.utils import BaseUserConfig, key_check, set_user_config


class ServerNameChangeType(TypedDict):
    ip: str
    port: int
    username: str
    password: str


class ServerNameChangeUserConfig(BaseUserConfig):
    KEY_NAME: ClassVar = "server_name_change_config"

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
    def save_to_db(values: ServerNameChangeType, dry_run=False):
        key_check(ServerNameChangeType.__required_keys__, values.keys())

        validated_conf = ServerNameChangeUserConfig(
            ip=values.get("ip"),
            port=values.get("port"),
            username=values.get("username"),
            password=values.get("password"),
        )

        if not dry_run:
            set_user_config(
                ServerNameChangeUserConfig.KEY(), validated_conf.model_dump()
            )
