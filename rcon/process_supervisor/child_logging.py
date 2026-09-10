"""Reconfigure inherited rcon.settings logging after fork (child env)."""

from __future__ import annotations

import copy
import logging
import os
import socket
from logging.config import dictConfig


def _close_all_handlers() -> None:
    loggers = [logging.root]
    loggers.extend(
        logger
        for logger in logging.root.manager.loggerDict.values()
        if isinstance(logger, logging.Logger)
    )
    for logger in loggers:
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            handler.close()


def configure_child_logging() -> None:
    import rcon.settings

    _close_all_handlers()
    cfg = copy.deepcopy(rcon.settings.LOGGING)
    filename = os.path.join(
        os.getenv("LOGGING_PATH", ""),
        os.getenv("LOGGING_FILENAME", f"{socket.gethostname()}.log"),
    )
    for handler in cfg.get("handlers", {}).values():
        class_name = handler.get("class", "")
        if class_name.endswith("FileHandler") and "filename" in handler:
            handler["filename"] = filename

    level = os.getenv("LOGGING_LEVEL", "DEBUG")
    commands_level = os.getenv("COMMANDS_LOGLEVEL", os.getenv("LOGGING_LEVEL", "INFO"))
    for logger_cfg in cfg.get("loggers", {}).values():
        if "level" not in logger_cfg:
            continue
        if "handlers" in logger_cfg:
            logger_cfg["level"] = level
        else:
            logger_cfg["level"] = commands_level
    dictConfig(cfg)
