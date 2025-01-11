import datetime
import logging
import os
import time

from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from rcon.logs.loop import LogLoop
from rcon.models import LogLine, PlayerID, enter_session
from rcon.types import StructuredLogLineWithMetaData
from rcon.utils import get_server_number

logger = logging.getLogger(__name__)

class LogRecorder:
    def __init__(self, dump_frequency_min=5, run_immediately=False):
        self.dump_frequency_min = dump_frequency_min
        self.run_immediately = run_immediately
        self.server_id = get_server_number()
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
        for log in LogLoop.get_log_history_list():
            if not isinstance(log, dict):
                logger.warning("Log is invalid, not a dict: %s", log)
                continue
            if (
                    not last_log
                    or int(log["timestamp_ms"]) / 1000 > last_log.event_time.timestamp()
            ):
                to_store.append(log)
            if (
                    last_log
                    and not int(log["timestamp_ms"]) / 1000
                            == last_log.event_time.timestamp()
                    and last_log.raw == log["raw"]
            ):
                logger.info("New logs collection at: %s", log)
                return to_store
        return to_store

    def _get_player_id_record(self, sess: Session, player_id: str):
        if not player_id:
            return None
        return (
            sess.query(PlayerID).filter(PlayerID.player_id == player_id).one_or_none()
        )

    def _save_logs(self, sess, to_store: list[StructuredLogLineWithMetaData]):
        for log in to_store:
            player_1 = self._get_player_id_record(sess, log["player_id_1"])
            player_2 = self._get_player_id_record(sess, log["player_id_2"])
            try:
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

    def run(self):
        last_run = datetime.datetime.now()
        if self.run_immediately:
            last_run = last_run - datetime.timedelta(minutes=self.dump_frequency_min)

        while True:
            now = datetime.datetime.now()
            if not (now - last_run).total_seconds() > self.dump_frequency_min * 60:
                logger.debug("Not due for recording yet")
                time.sleep(30)
                continue
            with enter_session() as sess:
                to_store = self._get_new_logs(sess)
                logger.info("%s log lines to record", len(to_store))

                self._save_logs(sess, to_store)

                last_run = datetime.datetime.now()
