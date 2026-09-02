"""Parse supervisord-style INI configuration for managed programs."""

from __future__ import annotations

import configparser
import os
import re
import shlex
from dataclasses import dataclass, field
from pathlib import Path

_ENV_INTERPOLATION = re.compile(r"%\(ENV_([A-Za-z0-9_]+)\)s")


def interpolate(value: str, environ: dict[str, str] | None = None) -> str:
    """Expand ``%(ENV_VARNAME)s`` placeholders using the arbiter environment."""

    env = environ if environ is not None else os.environ

    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in env:
            raise KeyError(f"Environment variable {key} is not set")
        return env[key]

    return _ENV_INTERPOLATION.sub(repl, value)


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_autorestart(value: str | None) -> str | bool:
    if value is None:
        return "unexpected"
    normalized = value.strip().lower()
    if normalized in {"true", "false"}:
        return normalized == "true"
    return normalized


def parse_environment(value: str | None) -> dict[str, str]:
    """Parse ``KEY=VAL,KEY2=VAL2`` program environment lines."""

    if not value:
        return {}

    result: dict[str, str] = {}
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        if "=" not in item:
            continue
        key, val = item.split("=", 1)
        result[key.strip()] = val.strip()
    return result


@dataclass
class ProgramConfig:
    name: str
    command: list[str]
    environment: dict[str, str] = field(default_factory=dict)
    autostart: bool = True
    autorestart: str | bool = "unexpected"
    startretries: int = 3
    startsecs: int = 1
    stopsignal: str = "TERM"
    stopwaitsecs: int = 10
    directory: str | None = None

    def child_environ(self, base_environ: dict[str, str] | None = None) -> dict[str, str]:
        env = dict(base_environ if base_environ is not None else os.environ)
        env.update(self.environment)
        return env

    def log_path(self, child_environ: dict[str, str]) -> Path:
        logging_path = child_environ.get("LOGGING_PATH", "/logs")
        logging_filename = child_environ.get("LOGGING_FILENAME")
        if logging_filename:
            return Path(logging_path) / logging_filename
        return Path(logging_path) / f"{self.name}.log"


def parse_byte_size(value: str) -> int:
    """Parse Supervisord-style size strings (e.g. ``50MB``) to bytes."""

    normalized = value.strip().upper()
    multipliers = {
        "KB": 1024,
        "MB": 1024**2,
        "GB": 1024**3,
    }
    for suffix, multiplier in multipliers.items():
        if normalized.endswith(suffix):
            number = normalized[: -len(suffix)].strip()
            return int(float(number) * multiplier)
    return int(normalized)


@dataclass
class SupervisorConfig:
    programs: dict[str, ProgramConfig]
    rpc_host: str = "0.0.0.0"
    rpc_port: int = 9001
    logfile: str | None = None
    logfile_maxbytes: int = 50 * 1024 * 1024
    logfile_backups: int = 10


def _split_command(command: str) -> list[str]:
    return shlex.split(command, posix=True)


def load_config(path: str | Path, environ: dict[str, str] | None = None) -> SupervisorConfig:
    """Load program definitions from a supervisord INI file."""

    env = dict(environ if environ is not None else os.environ)
    parser = configparser.ConfigParser(interpolation=None)
    parser.read(path)

    logfile: str | None = None
    logfile_maxbytes = 50 * 1024 * 1024
    logfile_backups = 10
    if parser.has_section("supervisord"):
        if parser.has_option("supervisord", "logfile"):
            logfile = interpolate(parser.get("supervisord", "logfile"), env)
        if parser.has_option("supervisord", "logfile_maxbytes"):
            logfile_maxbytes = parse_byte_size(
                parser.get("supervisord", "logfile_maxbytes")
            )
        if parser.has_option("supervisord", "logfile_backups"):
            logfile_backups = int(parser.get("supervisord", "logfile_backups"))

    rpc_host = "0.0.0.0"
    rpc_port = 9001
    if parser.has_section("inet_http_server") and parser.has_option(
        "inet_http_server", "port"
    ):
        port_value = interpolate(parser.get("inet_http_server", "port"), env)
        if ":" in port_value:
            host, port_str = port_value.rsplit(":", 1)
            rpc_host = host or "0.0.0.0"
            rpc_port = int(port_str)
        else:
            rpc_port = int(port_value)

    programs: dict[str, ProgramConfig] = {}
    for section in parser.sections():
        if not section.startswith("program:"):
            continue
        name = section.split(":", 1)[1]
        if not parser.has_option(section, "command"):
            continue

        raw_command = interpolate(parser.get(section, "command"), env)
        command = _split_command(raw_command)

        raw_environment = None
        if parser.has_option(section, "environment"):
            raw_environment = interpolate(parser.get(section, "environment"), env)
        environment = parse_environment(raw_environment)

        autostart = _parse_bool(
            parser.get(section, "autostart", fallback=None), default=True
        )
        autorestart = _parse_autorestart(
            parser.get(section, "autorestart", fallback=None)
        )
        startretries = int(parser.get(section, "startretries", fallback="3"))
        startsecs = int(parser.get(section, "startsecs", fallback="1"))
        stopsignal = parser.get(section, "stopsignal", fallback="TERM").upper()
        stopwaitsecs = int(parser.get(section, "stopwaitsecs", fallback="10"))

        directory = None
        if parser.has_option(section, "directory"):
            directory = interpolate(parser.get(section, "directory"), env)

        programs[name] = ProgramConfig(
            name=name,
            command=command,
            environment=environment,
            autostart=autostart,
            autorestart=autorestart,
            startretries=startretries,
            startsecs=startsecs,
            stopsignal=stopsignal,
            stopwaitsecs=stopwaitsecs,
            directory=directory,
        )

    return SupervisorConfig(
        programs=programs,
        rpc_host=rpc_host,
        rpc_port=rpc_port,
        logfile=logfile,
        logfile_maxbytes=logfile_maxbytes,
        logfile_backups=logfile_backups,
    )
