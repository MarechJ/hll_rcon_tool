"""Entry point for the CRCON process supervisor."""

from __future__ import annotations

import argparse
import logging
import os
import sys

from rcon.process_supervisor.config import load_config
from rcon.process_supervisor.logging_setup import configure_logging
from rcon.process_supervisor.manager import ProcessSupervisor
from rcon.process_supervisor.rpc import start_rpc_server


def _default_config_path() -> str:
    server_number = os.getenv("SERVER_NUMBER")
    if server_number:
        numbered = f"/config/supervisord_{server_number}.conf"
        if os.path.exists(numbered):
            return numbered
    return "/config/supervisord.conf"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CRCON process supervisor")
    parser.add_argument(
        "-c",
        "--config",
        default=_default_config_path(),
        help="Path to supervisord-style configuration file",
    )
    args = parser.parse_args(argv)

    if not os.path.exists(args.config):
        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s][%(levelname)s] %(name)s | %(message)s",
        )
        logging.error("Configuration file not found: %s", args.config)
        return 1

    config = load_config(args.config)
    configure_logging(config)
    logger = logging.getLogger(__name__)
    if config.logfile:
        logger.info("Arbiter logging to %s", config.logfile)

    supervisor = ProcessSupervisor(config)
    start_rpc_server(supervisor, config.rpc_host, config.rpc_port)
    return supervisor.run()


if __name__ == "__main__":
    sys.exit(main())
