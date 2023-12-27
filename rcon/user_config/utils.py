import logging
from typing import Any, Iterable, Self, Type

import pydantic
from sqlalchemy.exc import SQLAlchemyError

from rcon.cache_utils import invalidates, ttl_cache
from rcon.models import UserConfig, enter_session
from rcon.utils import get_server_number

logger = logging.getLogger(__name__)

USER_CONFIG_KEY_FORMAT = "{server}_{cls_name}"
DISCORD_AUDIT_FORMAT = "[{command_name}] changed values: {differences}"


# Sourced without modification from https://stackoverflow.com/a/17246726
def all_subclasses(cls):
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)]
    )


def key_check(mandatory_keys: frozenset, provided_keys: Iterable[str]):
    missing_keys = mandatory_keys - set(provided_keys)
    extra_keys = set(provided_keys) - mandatory_keys
    if extra_keys or missing_keys:
        raise InvalidKeysConfigurationError(
            missing_keys=set(missing_keys),
            extra_keys=set(extra_keys),
            mandatory_keys=set(mandatory_keys),
            provided_keys=set(provided_keys),
        )


class _listType(pydantic.BaseModel):
    """Used to raise ValidationErrors when not passed a list"""

    values: list[Any]


class InvalidKeysConfigurationError(Exception):
    """Raised for user configs that have extra or missing keys"""

    def __init__(
        self,
        missing_keys: set[str] = set(),
        extra_keys: set[str] = set(),
        mandatory_keys: set[str] = set(),
        provided_keys: set[str] = set(),
        *args: object,
    ) -> None:
        super().__init__(*args)
        self.missing_keys = missing_keys
        self.extra_keys = extra_keys
        self.mandatory_keys = mandatory_keys
        self.provided_keys = provided_keys

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"missing keys=({', '.join(self.missing_keys)}) | Extra keys = ({', '.join(self.extra_keys)}) | Mandatory keys=({', '.join(self.mandatory_keys)}) | Provided keys=({', '.join(self.provided_keys)})"

    def asdict(self):
        return {
            "type": InvalidKeysConfigurationError.__name__,
            "missing_keys": sorted([k for k in self.missing_keys]),
            "extra_keys": sorted([k for k in self.extra_keys]),
            "mandatory_keys": sorted([k for k in self.mandatory_keys]),
            "provided_keys": sorted([k for k in self.provided_keys]),
        }


class BaseUserConfig(pydantic.BaseModel):
    """The interface UI config settings should adhere to in addition to pydantic.BaseModel"""

    @classmethod
    def KEY(cls) -> str:
        """The database primary key for a setting"""
        return USER_CONFIG_KEY_FORMAT.format(
            server=get_server_number(), cls_name=cls.__name__
        )

    @classmethod
    def load_from_db(cls, default_on_error: bool = True) -> Self:
        # If the cache is unavailable, it will fall back to creating a default
        # model instance, but will not persist it to the database and overwrite settings
        conf = get_user_config(cls.KEY(), None)
        if conf is not None:
            try:
                return cls.model_validate(conf)
            except pydantic.ValidationError as e:
                if default_on_error:
                    logger.error(
                        f"Validation error loading {cls.KEY()}, returning defaults"
                    )
                    logger.error(e)
                    return cls()
                else:
                    raise
        else:
            logger.warning(f"{cls.KEY()} not found, creating defaults")
            conf = cls()
            set_user_config(conf.KEY(), conf.model_dump())

        return cls()

    @staticmethod
    def save_to_db() -> None:
        raise NotImplementedError


def _get_conf(sess, key):
    try:
        return sess.query(UserConfig).filter(UserConfig.key == key).one_or_none()
    except SQLAlchemyError as e:
        # Don't let a failed transaction block model creation
        # the session context manager will handle this
        sess.rollback()
        return None


def _get_user_config_cache_unavailable(
    key: str, default=None, cls: Type[BaseUserConfig] | None = None
) -> str | None:
    """Return a default model as JSON"""
    if cls:
        return cls().model_dump_json()
    else:
        raise ValueError(f"cls must not be None")


@ttl_cache(
    5 * 60 * 60,
    is_method=False,
    function_cache_unavailable=_get_user_config_cache_unavailable,
)
def get_user_config(
    key: str, default=None, cls: Type[BaseUserConfig] | None = None
) -> str | None:
    # cls required as a default parameter so it will be passed through to
    # _get_user_config_cache_unavailable in the ttl_cache decorator
    logger.debug("Getting user config for %s", key)
    with enter_session() as sess:
        res = _get_conf(sess, key)
        res = res.value if res else default
        logger.debug("User config for %s is %s", key, res)
        return res


def _add_conf(sess, key, val):
    try:
        return sess.add(UserConfig(key=key, value=val))
    except SQLAlchemyError as e:
        # Don't let a failed transaction block model creation
        # the session context manager will handle this
        sess.rollback()
        return None


def _remove_conf(sess, key):
    conf = _get_conf(sess, key)

    if conf is not None:
        logger.info("Deleting %s", key)
        sess.delete(conf)
        sess.commit()


def _set_default(sess, key, val):
    if _get_conf(sess, key) is None:
        _add_conf(sess, key, val)
    return val


def set_user_config(key, object_):
    with invalidates(get_user_config):
        logger.debug("Setting user config for %s with %s", key, object_)
        with enter_session() as sess:
            conf = _get_conf(sess, key)
            if conf is None:
                _add_conf(sess, key, object_)
            else:
                conf.value = object_
