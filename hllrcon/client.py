from collections.abc import Generator
from contextlib import contextmanager
import logging
import threading
from typing import Any

from hllrcon.connection import RconConnection, RconConnectionPool
from hllrcon.commands import RconCommands
from rcon.settings import RconCredentials


logger = logging.getLogger(__name__)


class RconClient(RconCommands):
    """An inferface for connecting to an RCON server."""

    def __init__(
        self, credentials: RconCredentials, max_conn_open=20, max_conn_idle=20
    ) -> None:
        """Initialize a new `Rcon` instance."""
        self.conn_pool = RconConnectionPool(
            credentials,
            max_conn_open,
            max_conn_idle,
        )

    @contextmanager
    def connect(self) -> Generator[RconConnection, None, None]:
        conn = self.conn_pool.get_connection()
        try:
            yield conn
        # TODO handle more specific exceptions?
        except Exception as e:
            logger.warning(
                "Connection (%s) errored in thread %s: %s, removing from pool",
                conn.id,
                threading.get_ident(),
                e,
            )
            self.conn_pool.close_connection(conn)
        else:
            self.conn_pool.return_connection(conn)

    def execute(
        self,
        command: str,
        version: int,
        body: str | dict[str, Any] = "",
    ) -> str:
        with self.connect() as connection:
            res = connection.send(command, version, body)
            res.raise_for_status()
            return res.content_body
