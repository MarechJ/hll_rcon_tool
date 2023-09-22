import logging
from typing import Any, ClassVar, Iterable, Self

import pydantic
from sqlalchemy.exc import InvalidRequestError

from rcon.models import UserConfig, enter_session
from rcon.utils import get_server_number

logger = logging.getLogger(__name__)


# Sourced without modification from https://stackoverflow.com/a/17246726
def all_subclasses(cls):
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)]
    )


def key_check(mandatory_keys: frozenset, provided_keys: Iterable[str]):
    missing_keys = mandatory_keys - set(provided_keys)
    extra_keys = set(provided_keys) - mandatory_keys
    if extra_keys or missing_keys:
        raise MissingKeysConfigurationError(
            missing_keys=set(missing_keys),
            mandatory_keys=set(mandatory_keys),
            provided_keys=set(provided_keys),
        )


class _listType(pydantic.BaseModel):
    """Used to raise ValidationErrors when not passed a list"""

    values: list[Any]


class MissingKeysConfigurationError(Exception):
    def __init__(
        self,
        missing_keys: set[str] = set(),
        mandatory_keys: set[str] = set(),
        provided_keys: set[str] = set(),
        *args: object,
    ) -> None:
        super().__init__(*args)
        self.missing_keys = missing_keys
        self.mandatory_keys = mandatory_keys
        self.provided_keys = provided_keys

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"missing keys=({', '.join(self.missing_keys)}) | Mandatory keys=({', '.join(self.mandatory_keys)}) | Provided keys=({', '.join(self.provided_keys)})"

    def asdict(self):
        return {
            "missing_keys": [k for k in self.missing_keys],
            "mandatory_keys": [k for k in self.mandatory_keys],
            "provided_keys": [k for k in self.provided_keys],
        }


class BaseUserConfig(pydantic.BaseModel):
    """The interface UI config settings should adhere to in addition to pydantic.BaseModel"""

    @classmethod
    def KEY(cls) -> str:
        """The database primary key for a setting"""
        return f"{get_server_number()}_{cls.__name__}"

    @classmethod
    def load_from_db(cls) -> Self:
        conf = get_user_config(cls.KEY(), None)

        if conf:
            return cls.model_validate(conf)
        else:
            logger.warning(f"{cls.KEY()} not found, returning defaults")

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
            try:
                _add_conf(sess, key, object_)
            except InvalidRequestError as e:
                # Don't let a previous failed transaction block future ones
                logger.exception(e)
                sess.rollback()
        else:
            conf.value = object_
        sess.commit()
