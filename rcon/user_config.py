import os
from dataclasses import dataclass, field, asdict
from typing import List
import logging

from sqlalchemy.sql.expression import false

from rcon.models import UserConfig, enter_session
from rcon.commands import CommandFailedError

logger = logging.getLogger(__name__)


def _get_conf(sess, key):
    return sess.query(UserConfig).filter(UserConfig.key == key).one_or_none()


def get_user_config(key, default=None):
    with enter_session() as sess:
        res = _get_conf(sess, key)
        return res.value if res else default


def _add_conf(sess, key, val):
    return sess.add(UserConfig(key=key, value=val))


def _set_default(sess, key, val):
    if _get_conf(sess, key) is None:
        _add_conf(sess, key, val)
    return val


def set_user_config(key, object_):
    with enter_session() as sess:
        conf = _get_conf(sess, key)
        if conf is None:
            _add_conf(sess, key, object_)
        else:
            conf.value = object_
        sess.commit()


class InvalidConfigurationError(Exception):
    pass


@dataclass
class Hook:
    roles: List[str] = field(default_factory=list)
    hook: str = None


@dataclass
class Hooks:
    name: str
    hooks: List[Hook] = field(default_factory=list)

    @classmethod
    def from_dict(cls, dict_):
        hooks = [Hook(**h) for h in dict_.pop("hooks", [])]
        return cls(hooks=hooks, **dict_)


class DiscordHookConfig:
    hooks_key = "discord_hooks"
    expected_hook_types = (
        "watchlist",
        "camera",
        # TODO
        # chat
        # kill
        # audit
    )

    def __init__(self, for_type):
        if for_type not in self.expected_hook_types:
            raise ValueError("Using unexpected hook type %s", for_type)
        server_number = os.getenv("SERVER_NUMBER", 0)
        self.for_type = for_type
        self.HOOKS_KEY = f"{server_number}_{self.hooks_key}_{for_type}"

    @staticmethod
    def get_all_hook_types(as_dict=False):
        hooks = []
        with enter_session() as sess:
            for name in DiscordHookConfig.expected_hook_types:
                hooks.append(asdict(DiscordHookConfig(for_type=name).get_hooks()))
            return hooks

    def get_hooks(self) -> Hooks:
        conf = get_user_config(self.HOOKS_KEY, None)
        if conf:
            return Hooks.from_dict(conf)
        return Hooks(name=self.for_type)

    def set_hooks(self, hooks):
        if not isinstance(hooks, list):
            raise InvalidConfigurationError("%s must be a list", self.HOOKS_KEY)
        hooks = Hooks(name=self.for_type, hooks=[Hook(**h) for h in hooks])
        set_user_config(self.HOOKS_KEY, asdict(hooks))


class CameraConfig:
    def __init__(self):
        server_number = os.getenv("SERVER_NUMBER", 0)
        self.BROADCAST = f"{server_number}_broadcast_camera"
        self.WELCOME = f"{server_number}_say_camera"

    def seed_db(self, sess):
        _set_default(sess, self.BROADCAST, False)
        _set_default(sess, self.WELCOME, False)

    def is_broadcast(self):
        return get_user_config(self.BROADCAST)

    def is_welcome(self):
        return get_user_config(self.WELCOME)

    def set_broadcast(self, bool_):
        return set_user_config(self.BROADCAST, bool(bool_))

    def set_welcome(self, bool_):
        return set_user_config(self.WELCOME, bool(bool_))


class AutoVoteKickConfig:
    def __init__(self):
        server_number = os.getenv("SERVER_NUMBER", 0)
        self.ENABLED = f"{server_number}_autovotekick_enabled"
        self.MIN_INGAME_MODS = f"{server_number}_autovotekick_min_mods_ingame"
        self.MIN_ONLINE_MODS = f"{server_number}_autovotekick_min_mods_online"
        self.CONDITION = f"{server_number}_autovotekick_condition"

    def seed_db(self, sess):
        _set_default(sess, self.ENABLED, False)
        _set_default(sess, self.MIN_INGAME_MODS, 1)
        _set_default(sess, self.MIN_ONLINE_MODS, 2)
        _set_default(sess, self.CONDITION, "OR")

    def is_enabled(self):
        return get_user_config(self.ENABLED)

    def get_min_ingame_mods(self):
        return int(get_user_config(self.MIN_INGAME_MODS))

    def get_min_online_mods(self):
        return int(get_user_config(self.MIN_ONLINE_MODS))

    def get_condition_type(self):
        return get_user_config(self.CONDITION)

    def set_is_enabled(self, value):
        return set_user_config(self.ENABLED, value)

    def set_min_ingame_mods(self, value):
        return set_user_config(self.MIN_INGAME_MODS, int(value))

    def set_min_online_mods(self, value):
        return set_user_config(self.MIN_ONLINE_MODS, int(value))

    def set_condition_type(self, value):
        return set_user_config(self.CONDITION, value)


class AutoBroadcasts:
    def __init__(self):
        server_number = os.getenv("SERVER_NUMBER", 0)
        self.BROADCASTS_RANDOMIZE = f"{server_number}_broadcasts_randomize"
        self.BROADCASTS_MESSAGES = f"{server_number}_broadcasts_messages"
        self.BROADCASTS_ENABLED = f"{server_number}_broadcasts_enabled"

    def seed_db(self, sess):
        _set_default(sess, self.BROADCASTS_RANDOMIZE, False)
        _set_default(sess, self.BROADCASTS_MESSAGES, [])
        _set_default(sess, self.BROADCASTS_ENABLED, False)

    def get_messages(self):
        return get_user_config(self.BROADCASTS_MESSAGES)

    def set_messages(self, messages):
        msgs = []

        for m in messages:
            m = m.replace("\\n", "\n")
            if isinstance(m, str):
                m = m.split(" ", 1)
            if len(m) != 2:
                raise InvalidConfigurationError(
                    "Broacast message must be tuples (<int: seconds>, <str: message>)"
                )
            time, msg = m
            try:
                time = int(time)
                if time <= 0:
                    raise ValueError("Negative")
            except ValueError as e:
                raise InvalidConfigurationError(
                    "Time must be an positive integer"
                ) from e
            msgs.append((time, msg))

        set_user_config(self.BROADCASTS_MESSAGES, msgs)

    def get_randomize(self):
        return get_user_config(self.BROADCASTS_RANDOMIZE)

    def set_randomize(self, bool_):
        if not isinstance(bool_, bool):
            raise InvalidConfigurationError("Radomize must be a boolean")
        return set_user_config(self.BROADCASTS_RANDOMIZE, bool_)

    def get_enabled(self):
        return get_user_config(self.BROADCASTS_ENABLED)

    def set_enabled(self, bool_):
        if not isinstance(bool_, bool):
            raise InvalidConfigurationError("Enabled must be a boolean")
        return set_user_config(self.BROADCASTS_ENABLED, bool_)


class StandardMessages:
    WELCOME = "standard_messages_welcome"
    BROADCAST = "standard_messages_broadcasts"
    PUNITIONS = "standard_messages_punitions"

    def __init__(self):
        self.message_types = {
            "welcome": self.WELCOME,
            "broadcast": self.BROADCAST,
            "punitions": self.PUNITIONS,
        }

    def seed_db(self, sess):
        fields = [self.BROADCAST, self.PUNITIONS, self.WELCOME]
        for field in fields:
            if _get_conf(sess, field) is None:
                _add_conf(sess, field, [])

    def get_messages(self, msg_type):
        try:
            return get_user_config(self.message_types[msg_type])
        except KeyError:
            raise CommandFailedError("{} is an invalid type".format(msg_type))

    def set_messages(self, msg_type, messages):
        msgs = []

        for m in messages:
            m = m.replace("\\n", "\n")
            m = m.strip()
            if m:
                msgs.append(m)
        try:
            set_user_config(self.message_types[msg_type], msgs)
        except KeyError:
            raise CommandFailedError("{} is an invalid type".format(msg_type))


def seed_default_config():
    with enter_session() as sess:
        AutoBroadcasts().seed_db(sess)
        StandardMessages().seed_db(sess)
        CameraConfig().seed_db(sess)
        AutoVoteKickConfig().seed_db(sess)
        sess.commit()
