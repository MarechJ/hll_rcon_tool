import enum
import logging
import os
import re
from collections.abc import Iterable
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, ClassVar, Self

import pydantic
from pydantic import ValidationInfo
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from rcon.game import get_game_profile
from rcon.game.base import GameProfile
from rcon.models import UserConfig, enter_session
from rcon.types import GameEnum, GameIntEnum, ServerInfo

logger = logging.getLogger(__name__)

USER_CONFIG_KEY_FORMAT = "{server}_{cls_name}"
USER_CONFIG_IDENTITY_FORMAT = "{game}_{server}_{name}"
DISCORD_AUDIT_FORMAT = "changed values: `{differences}`"

GameSelector = GameEnum | GameIntEnum | str | int
UserConfigScope = tuple[GameIntEnum, int]

_active_user_config_scope: ContextVar[UserConfigScope | None] = ContextVar(
    "active_user_config_scope", default=None
)


def get_user_config_game(game: GameSelector | None = None) -> GameIntEnum:
    """Resolve a database game ID, defaulting to the current process game."""
    if game is None:
        scope = _active_user_config_scope.get()
        if scope is not None:
            return scope[0]
        game = ServerInfo.from_env().game

    if isinstance(game, GameIntEnum):
        return game
    if isinstance(game, GameEnum):
        return game.to_int()
    if isinstance(game, int):
        return GameIntEnum(game)

    try:
        return GameEnum(game).to_int()
    except ValueError:
        return GameIntEnum(int(game))


def get_user_config_server_number(server_number: int | str | None = None) -> int:
    """Resolve a database server number, defaulting to SERVER_NUMBER."""
    if server_number is None:
        scope = _active_user_config_scope.get()
        if scope is not None:
            return scope[1]
        server_number = ServerInfo.from_env().number
    if server_number is None:
        raise ValueError("SERVER_NUMBER is not set")
    return int(server_number)


def server_info_for_rcon(rcon: Any | None = None) -> ServerInfo:
    """Resolve config scope from the process server and an RCON game profile."""
    bound_server_info = getattr(rcon, "server_info", None)
    if isinstance(bound_server_info, ServerInfo):
        return bound_server_info

    server_info = ServerInfo.from_env()
    rcon_game = getattr(getattr(rcon, "game_profile", None), "game", None)
    if isinstance(rcon_game, GameEnum):
        server_info.game = rcon_game
    return server_info


@contextmanager
def user_config_scope(
    *,
    game: GameSelector | None = None,
    server_number: int | str | None = None,
):
    """Propagate a config identity through legacy model save implementations."""
    scope = (
        get_user_config_game(game),
        get_user_config_server_number(server_number),
    )
    token = _active_user_config_scope.set(scope)
    try:
        yield scope
    finally:
        _active_user_config_scope.reset(token)


def user_config_identity(
    name: str,
    *,
    game: GameSelector | None = None,
    server_number: int | str | None = None,
) -> tuple[GameIntEnum, int, str]:
    """Return the canonical database identity for a user config."""
    return (
        get_user_config_game(game),
        get_user_config_server_number(server_number),
        name,
    )


def user_config_validation_context(
    *,
    game: GameSelector | None = None,
    server_number: int | str | None = None,
) -> dict[str, GameEnum | int]:
    """Build Pydantic context for game-aware config validators."""
    game_id = get_user_config_game(game)
    return {
        "game": GameEnum.from_int(game_id),
        "game_id": game_id,
        "server_number": get_user_config_server_number(server_number),
    }


def game_profile_from_validation_info(info: ValidationInfo) -> GameProfile:
    """Resolve the game profile supplied to a Pydantic validation run."""
    context = info.context or {}
    game = context.get("game")
    if game is None:
        game = GameEnum.from_int(get_user_config_game())
    return get_game_profile(game)


def validate_game_roles(values: Iterable[str], info: ValidationInfo) -> list[str]:
    """Validate role IDs against the selected game's role catalog."""
    roles = [
        str(value.value) if isinstance(value, enum.Enum) else str(value)
        for value in values
    ]
    profile = game_profile_from_validation_info(info)
    invalid_roles = sorted(set(roles) - profile.roles)
    if invalid_roles:
        raise ValueError(
            f"Roles are not valid for {profile.game.value}: " + ", ".join(invalid_roles)
        )
    return roles


def _normalize_weapon_id(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def validate_game_weapons(values: Iterable[str], info: ValidationInfo) -> list[str]:
    """Reject weapon IDs known to belong only to a different game."""
    weapons = [str(value) for value in values]
    profile = game_profile_from_validation_info(info)
    valid_weapon_ids = {
        _normalize_weapon_id(value) for value in profile.valid_weapon_ids
    }
    all_known_weapon_ids = {
        _normalize_weapon_id(value)
        for game in GameEnum
        for value in get_game_profile(game).valid_weapon_ids
    }
    invalid_weapons = sorted(
        value
        for value in set(weapons)
        if _normalize_weapon_id(value) in all_known_weapon_ids
        and _normalize_weapon_id(value) not in valid_weapon_ids
    )
    if invalid_weapons:
        raise ValueError(
            f"Weapons are not valid for {profile.game.value}: "
            + ", ".join(invalid_weapons)
        )
    return weapons


# Sourced without modification from https://stackoverflow.com/a/17246726
def all_subclasses(cls):
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)]
    )


def key_check(
    mandatory_keys: frozenset, optional_keys: frozenset, provided_keys: Iterable[str]
):
    missing_keys = mandatory_keys - set(provided_keys)
    extra_keys = set(provided_keys) - mandatory_keys - optional_keys
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
        missing_keys: set[str] | None = None,
        extra_keys: set[str] | None = None,
        mandatory_keys: set[str] | None = None,
        provided_keys: set[str] | None = None,
        *args: object,
    ) -> None:
        super().__init__(*args)
        self.missing_keys = missing_keys or set()
        self.extra_keys = extra_keys or set()
        self.mandatory_keys = mandatory_keys or set()
        self.provided_keys = provided_keys or set()

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"missing keys=({', '.join(self.missing_keys)}) | Extra keys = ({', '.join(self.extra_keys)}) | Mandatory keys=({', '.join(self.mandatory_keys)}) | Provided keys=({', '.join(self.provided_keys)})"

    def asdict(self) -> dict[str, Any]:
        return {
            "type": InvalidKeysConfigurationError.__name__,
            "missing_keys": sorted([k for k in self.missing_keys]),
            "extra_keys": sorted([k for k in self.extra_keys]),
            "mandatory_keys": sorted([k for k in self.mandatory_keys]),
            "provided_keys": sorted([k for k in self.provided_keys]),
        }


class BaseUserConfig(pydantic.BaseModel):
    """The interface UI config settings should adhere to in addition to pydantic.BaseModel"""

    NAME: ClassVar[str]

    @classmethod
    def load_from_db(
        cls,
        default_on_validation_error: bool = True,
        *,
        game: GameSelector | None = None,
        server_number: int | str | None = None,
    ) -> Self:
        # This should never happen in production, but allows tests to run
        if not os.getenv("HLL_DB_URL"):
            logger.warning("HLL_DB_URL not set, returning a default instance")
            return cls()

        # If the cache is unavailable, it will fall back to creating a default
        # model instance, but will not persist it to the database and overwrite settings
        conf = get_user_config(
            cls.NAME,
            default=None,
            game=game,
            server_number=server_number,
        )
        if conf is not None:
            try:
                return cls.model_validate(
                    conf,
                    context=user_config_validation_context(
                        game=game,
                        server_number=server_number,
                    ),
                )
            except pydantic.ValidationError as e:
                if default_on_validation_error:
                    logger.error(
                        f"Error loading {cls.identity(game=game, server_number=server_number)}, "
                        "returning defaults, validation errors:"
                    )
                    logger.error(e)
                    return cls()
                else:
                    raise
        else:
            # This shouldn't happen because we seed the database on startup if the
            # records don't exist, if someone has manually edited their database that
            # is on them, previously we would not seed defaults and create/persist an
            # instance if `get_user_config` did not find a record for any reason.
            # This was resetting peoples legitimate configs in some scenarios, particularly
            # when containers were being created/torn down and a service or the backend queried
            # a model and postgres was unavailable.
            # Now models are only persisted to the database when they're either explicitly seeded
            # during backend startup, or if the `save_to_db` method is explicitly called, for
            # instance through the API, or CLI
            logger.error(
                "%s not found, returning defaults",
                cls.identity(game=game, server_number=server_number),
            )

        return cls()

    @staticmethod
    def save_to_db(values: dict[str, Any], dry_run: bool) -> None:
        raise NotImplementedError

    @classmethod
    def identity(
        cls,
        *,
        game: GameSelector | None = None,
        server_number: int | str | None = None,
    ) -> str:
        game_id, server, name = user_config_identity(
            cls.NAME, game=game, server_number=server_number
        )
        return USER_CONFIG_IDENTITY_FORMAT.format(
            game=int(game_id), server=server, name=name
        )

    @classmethod
    def seed_db(
        cls,
        sess: Session,
        *,
        game: GameSelector | None = None,
        server_number: int | str | None = None,
    ):
        _set_default(
            sess,
            name=cls.NAME,
            val=cls(),
            game=game,
            server_number=server_number,
        )


def _get_conf(
    sess: Session,
    name: str,
    *,
    game: GameSelector | None = None,
    server_number: int | str | None = None,
):
    game_id, server, name = user_config_identity(
        name, game=game, server_number=server_number
    )
    try:
        return (
            sess.query(UserConfig)
            .filter(
                UserConfig.game == int(game_id),
                UserConfig.server_number == server,
                UserConfig.name == name,
            )
            .one_or_none()
        )
    except SQLAlchemyError:
        # Don't let a failed transaction block model creation
        # the session context manager will handle this
        sess.rollback()
        return None


def get_user_config(
    name: str,
    default=None,
    *,
    game: GameSelector | None = None,
    server_number: int | str | None = None,
) -> dict[str, Any] | Any | None:
    with enter_session() as sess:
        res = _get_conf(sess, name, game=game, server_number=server_number)
        res = res.value if res else default
        return res


def _add_conf(
    sess: Session,
    name: str,
    val,
    *,
    game: GameSelector | None = None,
    server_number: int | str | None = None,
):
    game_id, server, name = user_config_identity(
        name, game=game, server_number=server_number
    )
    try:
        return sess.add(
            UserConfig(
                game=int(game_id),
                server_number=server,
                name=name,
                value=val,
            )
        )
    except SQLAlchemyError:
        # Don't let a failed transaction block model creation
        # the session context manager will handle this
        sess.rollback()
        return None


def _remove_conf(
    sess: Session,
    name: str,
    *,
    game: GameSelector | None = None,
    server_number: int | str | None = None,
):
    conf = _get_conf(sess, name, game=game, server_number=server_number)

    if conf is not None:
        logger.info(
            "Deleting %s",
            USER_CONFIG_IDENTITY_FORMAT.format(
                game=conf.game,
                server=conf.server_number,
                name=conf.name,
            ),
        )
        sess.delete(conf)
        sess.commit()


def _set_default(
    sess: Session,
    name: str,
    val: dict[str, Any] | BaseUserConfig,
    *,
    game: GameSelector | None = None,
    server_number: int | str | None = None,
):
    if isinstance(val, BaseUserConfig):
        val = val.model_dump()

    if _get_conf(sess, name, game=game, server_number=server_number) is None:
        game_id, server, name = user_config_identity(
            name, game=game, server_number=server_number
        )
        logger.info(
            "Seeding default values for %s",
            USER_CONFIG_IDENTITY_FORMAT.format(
                game=int(game_id), server=server, name=name
            ),
        )
        _add_conf(
            sess,
            name,
            val,
            game=game_id,
            server_number=server,
        )
    return val


def set_user_config(
    name: str,
    object_: dict[str, Any] | BaseUserConfig,
    *,
    game: GameSelector | None = None,
    server_number: int | str | None = None,
):
    if isinstance(object_, BaseUserConfig):
        object_ = object_.model_dump()

    game_id, server, name = user_config_identity(
        name, game=game, server_number=server_number
    )
    identity = USER_CONFIG_IDENTITY_FORMAT.format(
        game=int(game_id), server=server, name=name
    )
    logger.debug("Setting user config for %s with %s", identity, object_)
    with enter_session() as sess:
        conf = _get_conf(sess, name, game=game_id, server_number=server)
        if conf is None:
            _add_conf(
                sess,
                name,
                object_,
                game=game_id,
                server_number=server,
            )
        else:
            conf.value = object_


def validate_user_config(
    model: type[BaseUserConfig],
    data: dict[str, Any] | BaseUserConfig,
    dry_run: bool = True,
    reset_to_default: bool = False,
    *,
    game: GameSelector | None = None,
    server_number: int | str | None = None,
) -> None:
    with user_config_scope(game=game, server_number=server_number) as scope:
        game_id, server = scope
        # Run the complete model through Pydantic with scope context before any
        # model-specific compatibility transformations or persistence occur.
        model.model_validate(
            data,
            context=user_config_validation_context(
                game=game_id,
                server_number=server,
            ),
        )

        if reset_to_default:
            default = model()
            set_user_config(default.NAME, default)

        model.save_to_db(values=data, dry_run=dry_run)


def mask_sensitive_data(
    values: dict[str, Any],
    sensitive_keys: set[str] | None = None,
    masked_value: str = "***",
) -> None:
    if sensitive_keys is None:
        sensitive_keys = {
            "discord_webhook_url",
            "username",
            "password",
            "url",
            "webhook_urls",
            "api_key",
        }

    """Replace the value of any dict key in sensitive_keys with masked_value"""
    if not isinstance(values, dict):
        return

    for k, v in values.items():
        if isinstance(v, dict):
            mask_sensitive_data(v, sensitive_keys=sensitive_keys)
        elif isinstance(v, list):
            for ele in v:
                mask_sensitive_data(ele, sensitive_keys=sensitive_keys)

        if k in sensitive_keys:
            values[k] = masked_value
