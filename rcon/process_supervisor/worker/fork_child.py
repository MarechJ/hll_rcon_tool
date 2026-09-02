"""Forked worker child entry (no new interpreter)."""

from __future__ import annotations

import logging
import os
import sys

logger = logging.getLogger(__name__)


def reset_inherited_resources() -> None:
    import rcon.cache_utils
    import rcon.models

    engine = rcon.models._ENGINE
    if engine is not None:
        engine.dispose(close=False)
        rcon.models._ENGINE = None

    rcon.cache_utils._REDIS_POOL = None
    rcon.cache_utils._GLOBAL_REDIS_POOL = None
    # Fresh interpreters create this pool via ttl_cache(decode_responses=False)
    # before get_redis_client() (default True). Recreate that order after fork.
    rcon.cache_utils.get_redis_pool(decode_responses=False)


def _redirect_stdio(log_path: str) -> None:
    fd = os.open(log_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    os.dup2(fd, 1)
    os.dup2(fd, 2)
    if fd not in {1, 2}:
        os.close(fd)


def fork_main(
    name: str,
    extra: list[str],
    env: dict[str, str],
    log_path: str,
    directory: str | None,
) -> None:
    try:
        os.environ.clear()
        os.environ.update(env)
        os.setsid()
        _redirect_stdio(log_path)
        if directory:
            os.chdir(directory)

        import rcon.settings  # noqa: F401

        from rcon.models import install_unaccent

        install_unaccent()
        reset_inherited_resources()

        from rcon.process_supervisor.registry import run_program

        run_program(name, extra)
    except SystemExit as exc:
        code = exc.code
        if code is None:
            os._exit(0)
        if isinstance(code, int):
            os._exit(code)
        os._exit(1)
    except Exception:
        logger.exception("Forked worker %r failed", name)
        os._exit(1)

    os._exit(0)


if __name__ == "__main__":
    sys.exit(0)
