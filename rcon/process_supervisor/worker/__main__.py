"""Run a registered supervisord program without importing rcon.cli."""

from __future__ import annotations

import logging
import sys

logger = logging.getLogger(__name__)


def _parse_argv(argv: list[str]) -> tuple[str, list[str]]:
    if not argv:
        raise SystemExit("usage: python -m rcon.process_supervisor.worker NAME [-- extra...]")

    if "--" in argv:
        separator = argv.index("--")
        name = argv[0]
        extra = argv[separator + 1 :]
        return name, extra

    return argv[0], argv[1:]


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    name, extra = _parse_argv(args)

    import rcon.settings  # noqa: F401 - configures logging from child env
    from rcon.models import install_unaccent
    from rcon.process_supervisor.registry import run_program

    install_unaccent()

    try:
        run_program(name, extra)
    except KeyError:
        logger.exception("Unknown worker program %r", name)
        return 1
    except SystemExit as exc:
        code = exc.code
        if code is None:
            return 0
        if isinstance(code, int):
            return code
        return 1
    except Exception:
        logger.exception("Worker %r failed", name)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
