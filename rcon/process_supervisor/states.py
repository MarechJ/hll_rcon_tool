"""Supervisord-compatible process state codes."""

from __future__ import annotations

from enum import IntEnum


class ProcessState(IntEnum):
    STOPPED = 0
    STARTING = 10
    RUNNING = 20
    BACKOFF = 30
    STOPPING = 40
    EXITED = 50
    FATAL = 100
    UNKNOWN = 1000


STATENAME: dict[ProcessState, str] = {state: state.name for state in ProcessState}

# Supervisord XML-RPC fault codes used by the CRCON UI.
FAULT_BAD_NAME = 10
FAULT_ALREADY_STARTED = 60
FAULT_NOT_RUNNING = 70
