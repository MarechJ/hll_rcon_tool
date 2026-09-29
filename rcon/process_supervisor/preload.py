"""Forkserver preload configuration for CoW worker children."""

from __future__ import annotations

import multiprocessing
import os
import sys
from typing import Any

PRELOAD_MODULES: tuple[str, ...] = ("hllrcon", "rcon.maps")

_FORKSERVER_CONTEXT: Any | None = None

_DISABLED_VALUES = frozenset({"0", "false", "no", "off"})


def fork_enabled() -> bool:
    if sys.platform == "win32":
        return False
    value = os.environ.get("CRCON_SUPERVISOR_FORK", "1").strip().lower()
    return value not in _DISABLED_VALUES


def ensure_forkserver() -> Any:
    global _FORKSERVER_CONTEXT

    if _FORKSERVER_CONTEXT is not None:
        return _FORKSERVER_CONTEXT

    multiprocessing.set_forkserver_preload(list(PRELOAD_MODULES))
    _FORKSERVER_CONTEXT = multiprocessing.get_context("forkserver")
    return _FORKSERVER_CONTEXT
