import logging
from typing import Iterable, Self

import pydantic

from rcon.models import UserConfig, enter_session
from rcon.utils import get_server_number

logger = logging.getLogger(__name__)


def key_check(mandatory_keys: frozenset, provided_keys: Iterable[str]):
    missing_keys = mandatory_keys - set(provided_keys)
    if missing_keys:
        raise InvalidConfigurationError(
            f"missing keys=({', '.join(missing_keys)}) | Mandatory keys=({', '.join(mandatory_keys)}) | Provided keys=({', '.join(provided_keys)})"
        )


class InvalidConfigurationError(Exception):
    pass


class BaseUserConfig(pydantic.BaseModel):
    """The interface UI config settings should adhere to in addition to pydantic.BaseModel"""

    KEY_NAME: str = pydantic.Field(default="")

    @classmethod
    def KEY(cls) -> str:
        """The database primary key for a setting"""
        return f"{get_server_number()}_{cls.KEY_NAME}"

    @classmethod
    def load_from_db(cls) -> Self:
        conf = get_user_config(cls.KEY(), None)

        if conf:
            return cls.model_validate(conf)

        from pprint import pprint

        # pprint(cls)
        # pprint(cls().model_dump())
        # pprint(cls().model_dump_json())

        return cls()

    @staticmethod
    def save_to_db() -> None:
        raise NotImplementedError


def _get_conf(sess, key):
    return sess.query(UserConfig).filter(UserConfig.key == key).one_or_none()


def get_user_config(key, default=None) -> bool:
    logger.debug("Getting user config for %s", key)
    with enter_session() as sess:
        res = _get_conf(sess, key)
        res = res.value if res else default
        logger.debug("User config for %s is %s", key, res)
        return res


def _add_conf(sess, key, val):
    return sess.add(UserConfig(key=key, value=val))


def _set_default(sess, key, val):
    if _get_conf(sess, key) is None:
        _add_conf(sess, key, val)
    return val


def set_user_config(key, object_):
    logger.debug("Setting user config for %s with %s", key, object_)
    with enter_session() as sess:
        conf = _get_conf(sess, key)
        if conf is None:
            _add_conf(sess, key, object_)
        else:
            conf.value = object_
        sess.commit()
