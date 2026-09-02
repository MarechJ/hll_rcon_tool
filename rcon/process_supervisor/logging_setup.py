"""Configure arbiter logging to stderr and optional supervisord logfile."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from rcon.process_supervisor.config import SupervisorConfig

_LOG_FORMAT = "[%(asctime)s][%(levelname)s] %(name)s | %(message)s"
_SUPERVISOR_LOGGER = "rcon.process_supervisor"
_CHILD_LOGGERS = (
    f"{_SUPERVISOR_LOGGER}.process",
    f"{_SUPERVISOR_LOGGER}.manager",
    f"{_SUPERVISOR_LOGGER}.rpc",
    f"{_SUPERVISOR_LOGGER}.__main__",
)


def configure_logging(config: SupervisorConfig) -> None:
    formatter = logging.Formatter(_LOG_FORMAT)

    stderr_handler = logging.StreamHandler()
    stderr_handler.setFormatter(formatter)

    file_handler: RotatingFileHandler | None = None
    if config.logfile:
        log_path = Path(config.logfile)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            config.logfile,
            maxBytes=config.logfile_maxbytes,
            backupCount=config.logfile_backups,
        )
        file_handler.setFormatter(formatter)

    supervisor_logger = logging.getLogger(_SUPERVISOR_LOGGER)
    supervisor_logger.handlers.clear()
    supervisor_logger.setLevel(logging.INFO)
    supervisor_logger.propagate = False
    supervisor_logger.addHandler(stderr_handler)
    if file_handler is not None:
        supervisor_logger.addHandler(file_handler)

    for name in _CHILD_LOGGERS:
        child = logging.getLogger(name)
        child.handlers.clear()
        child.propagate = True
