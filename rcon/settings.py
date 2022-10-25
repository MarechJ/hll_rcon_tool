import logging
import os
import socket
from logging.config import dictConfig

# TODO: Use a config style that is not required at import time

SERVER_INFO = {
    "host": os.getenv("HLL_HOST"),
    "port": os.getenv("HLL_PORT"),
    "password": os.getenv("HLL_PASSWORD"),
}


def check_config():
    for k, v in SERVER_INFO.items():
        if not v:
            raise ValueError(f"{k} environment variable must be set")
    try:
        SERVER_INFO["port"] = int(SERVER_INFO["port"])
    except ValueError as e:
        raise ValueError("HLL_PORT must be an integer") from e


# TODO add sentry
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {
            "format": "[%(asctime)s][%(levelname)s] %(name)s "
            "%(filename)s:%(funcName)s:%(lineno)d | %(message)s",
        },
    },
    "handlers": {
        "console": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "console"},
        "file": {
            "level": "DEBUG",
            "formatter": "console",
            "class": "logging.FileHandler",
            "filename": os.path.join(
                os.getenv("LOGGING_PATH", ""),
                os.getenv("LOGGING_FILENAME", f"{socket.gethostname()}.log"),
            ),
        },
        "team_balance_file": {
            "level": "DEBUG",
            "formatter": "console",
            "class": "logging.FileHandler",
            "filename": os.path.join(
                os.getenv("LOGGING_PATH", ""),
                os.getenv(
                    "LOGGING_FILENAME",
                    f"team_balance_{os.getenv('SERVER_NUMBER', '')}.log",
                ),
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
        "rcon.extended_commands": {"level": os.getenv("COMMANDS_LOGLEVEL", os.getenv("LOGGING_LEVEL", "INFO"))},
        "rcon.recorded_commands": {"level": os.getenv("COMMANDS_LOGLEVEL", os.getenv("LOGGING_LEVEL", "INFO"))},
        "rcon.commands": {"level": os.getenv("COMMANDS_LOGLEVEL", os.getenv("LOGGING_LEVEL", "INFO"))},
        # TODO fix that
        "rcon.squad_automod.automod": {
            "handlers": ["console", "file"],
            "level": os.getenv("LOGGING_LEVEL", "DEBUG"),
            "propagate": False,
        },
        "rcon.team_balance": {
            "handlers": ["console", "team_balance_file"],
            "level": os.getenv("LOGGING_LEVEL", "DEBUG"),
            "filename": "rcon.team_balance",
            "propagate": False,
        },
    },
}

dictConfig(LOGGING)
