import datetime
import logging
import os
import time
from typing import Callable, Iterable

from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from rcon.logs.loop import LogLoop
from rcon.models import LogLine, PlayerID, enter_session
from rcon.types import StructuredLogLineWithMetaData
from rcon.utils import get_server_number

logger = logging.getLogger(__name__)

class LogRecorder:
    def __init__(self, dump_frequency_seconds=10, log_history_fn: Callable[[], Iterable[StructuredLogLineWithMetaData]] = LogLoop.get_log_history_list):
        self.dump_frequency_seconds = dump_frequency_seconds
        self.server_id = get_server_number()
        self.log_history_fn = log_history_fn
        if not self.server_id:
            raise ValueError("SERVER_NUMBER is not set, can't record logs")

    def _get_new_logs(self, sess):
        to_store: list[StructuredLogLineWithMetaData] = []
        last_log = (
            sess.query(LogLine)
            .filter(LogLine.server == self.server_id)
            .order_by(desc(LogLine.event_time))
            .limit(1)
            .one_or_none()
        )
        logger.info("Getting new logs from %s", last_log.event_time if last_log else 0)
        log: StructuredLogLineWithMetaData
        for log in self.log_history_fn():
            if not isinstance(log, dict):
                logger.warning("Log is invalid, not a dict: %s", log)
                continue
            if last_log and int(log["timestamp_ms"]) / 1000 == last_log.event_time.timestamp() and '] ' + log["line_without_time"] in last_log.raw:
                break
            to_store.append(log)
        return to_store

    def _collect_player_ids(self, sess: Session, logs: list[StructuredLogLineWithMetaData]) -> dict[str, PlayerID | None]:
        players: dict[str, PlayerID | None] = {}
        for log in logs:
            if log["player_id_1"] is not None:
                players.setdefault(log["player_id_1"], None)
            if log["player_id_2"] is not None:
                players.setdefault(log["player_id_2"], None)
        player_ids = sess.query(PlayerID).filter(PlayerID.player_id.in_(list(players.keys())))
        for pid in player_ids:
            players[pid.player_id] = pid

        return players

    def _save_logs(self, sess, to_store: list[StructuredLogLineWithMetaData]):
        players = self._collect_player_ids(sess, to_store)

        for log in to_store:
            try:
                player_1: PlayerID | None = None
                player_2: PlayerID | None = None
                if log["player_id_1"]:
                    player_1 = players[log["player_id_1"]]
                if log["player_id_2"]:
                    player_2 = players[log["player_id_2"]]
                sess.add(
                    LogLine(
                        version=log["version"],
                        event_time=datetime.datetime.fromtimestamp(
                            log["timestamp_ms"] // 1000
                        ),
                        type=log["action"],
                        player1_name=log["player_name_1"],
                        player2_name=log["player_name_2"],
                        player_1=player_1,
                        player_2=player_2,
                        raw=log["raw"],
                        content=log["message"],
                        server=os.getenv("SERVER_NUMBER"),
                        weapon=log["weapon"],
                    )
                )
                sess.commit()
            except IntegrityError:
                sess.rollback()
                logger.exception("Unable to recorder %s", log)

    def run(self, run_immediately=False, one_off=False):
        last_run = datetime.datetime.now()
        if run_immediately or one_off:
            last_run = last_run - datetime.timedelta(seconds=self.dump_frequency_seconds + 1)

        while True:
            now = datetime.datetime.now()
            if not (now - last_run).total_seconds() > self.dump_frequency_seconds:
                logger.debug("Not due for recording yet")
                time.sleep(5)
                continue
            with enter_session() as sess:
                to_store = self._get_new_logs(sess)
                logger.info("%s log lines to record", len(to_store))

                self._save_logs(sess, to_store)

                last_run = datetime.datetime.now()
            if one_off:
                break
