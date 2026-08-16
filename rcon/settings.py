import os
import re
import socket
from logging.config import dictConfig
from subprocess import run

from rcon.types import ServerInfo
from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig

try:
    TAG_VERSION = (
        run(["git", "describe", "--tags"], check=False, capture_output=True)
        .stdout.decode()
        .strip()
    )
except Exception: # noqa
    TAG_VERSION = "unknown"

try:
    config = RconServerSettingsUserConfig.load_from_db()
    ENVIRONMENT = re.sub("[^0-9a-zA-Z]+", "", (config.short_name or "default").strip())[
        :64
    ]
except Exception: # noqa
    ENVIRONMENT = "undefined"



def get_server_info() -> ServerInfo:
    return ServerInfo.from_env()


def check_config() -> ServerInfo:
    server_info = get_server_info()
    for k, v in server_info.as_dict().items():
        if not v:
            raise ValueError(f"{k} environment variable must be set")
    return server_info


# TODO add sentry
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {
            "()": "colorlog.ColoredFormatter",
            "format": (
                f"[%(asctime)s][%(log_color)s%(levelname)s%(reset)s][{ENVIRONMENT}][{TAG_VERSION}] "
                "%(name)s %(filename)s:%(funcName)s:%(lineno)d | %(message)s"
            ),
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
            "style": "%",
        },
        "file": {
            "format": (
                f"[%(asctime)s][%(levelname)s][{ENVIRONMENT}][{TAG_VERSION}] "
                "%(name)s %(filename)s:%(funcName)s:%(lineno)d | %(message)s"
            ),
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "console",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "formatter": "file",
            "filename": os.path.join(
                os.getenv("LOGGING_PATH", ""),
                os.getenv("LOGGING_FILENAME", f"{socket.gethostname()}.log"),
            ),
        },
    },
    "loggers": {
        __package__: {
            "handlers": ["console", "file"],
            "level": os.getenv("LOGGING_LEVEL", "DEBUG"),
            "propagate": False,
        },
        "__main__": {
            "handlers": ["console", "file"],
            "level": os.getenv("LOGGING_LEVEL", "DEBUG"),
            "propagate": False,
        },
        "rcon.rcon": {
            "level": os.getenv("COMMANDS_LOGLEVEL", os.getenv("LOGGING_LEVEL", "INFO")),
        },
        "rcon.commands": {
            "level": os.getenv("COMMANDS_LOGLEVEL", os.getenv("LOGGING_LEVEL", "INFO")),
        },
        # TODO fix that
        "rcon.automods.automod": {
            "handlers": ["console", "file"],
            "level": os.getenv("LOGGING_LEVEL", "DEBUG"),
            "propagate": False,
        },
    },
}

dictConfig(LOGGING)
