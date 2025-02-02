import datetime

import pytest
from sqlalchemy.orm import Session

from rcon.logs.recorder import LogRecorder
from rcon.models import LogLine, enter_session, PlayerID


first_player_id = "76561198091327692"
second_player_id = "76561198133214514"

def ensure_player_id(sess: Session, player_id: str):
    if sess.query(PlayerID).where(PlayerID.player_id == player_id).one_or_none() is None:
        player = PlayerID(player_id=player_id)
        sess.add(player)

@pytest.fixture()
def log_recorder():
    with enter_session() as sess:
        sess.query(LogLine).delete()
        ensure_player_id(sess, first_player_id)
        ensure_player_id(sess, second_player_id)
    yield

class TestLogRecorder:
    def test_records_recent_logs(self, log_recorder):
        r = LogRecorder(log_history_fn=lambda: [{
            "version": 1,
            "timestamp_ms": 1612695641000,
            "event_time": datetime.datetime.fromtimestamp(1612695641),
            "action": "TEAM KILL",
            "player_name_1": "[ARC] DYDSO ★ツ",
            "player_id_1": first_player_id,
            "player_name_2": "Francky Mc Fly",
            "player_id_2": second_player_id,
            "weapon": "G43",
            "message": "",
            "raw": f"[646 ms (1612695641)] TEAM KILL: [ARC] DYDSO ★ツ(Axis/{first_player_id}) -> Francky Mc Fly(Axis/{second_player_id}) with None",
            "content": f"[ARC] DYDSO ★ツ(Axis/{first_player_id}) -> Francky Mc Fly(Axis/{second_player_id}) with None",
        }])
        with enter_session() as sess:
            r.run(run_immediately=True, one_off=True)

            res = sess.query(LogLine).all()
            first_player = sess.query(PlayerID).where(PlayerID.player_id == first_player_id).one()
            assert len(res) == 1
            assert res[0].player_1 == first_player
            assert res[0].player_2.player_id == second_player_id

    def test_no_duplicate_records(self, log_recorder):
        logs = [{
            "version": 1,
            "timestamp_ms": 1612695641000,
            "event_time": datetime.datetime.fromtimestamp(1612695641),
            "action": "TEAM KILL",
            "player_name_1": "[ARC] DYDSO ★ツ",
            "player_id_1": first_player_id,
            "player_name_2": "Francky Mc Fly",
            "player_id_2": second_player_id,
            "weapon": "G43",
            "message": "",
            "raw": f"[646 ms (1612695641)] TEAM KILL: [ARC] DYDSO ★ツ(Axis/{first_player_id}) -> Francky Mc Fly(Axis/{second_player_id}) with None",
            "content": f"[ARC] DYDSO ★ツ(Axis/{first_player_id}) -> Francky Mc Fly(Axis/{second_player_id}) with None",
        }]
        r = LogRecorder(log_history_fn=lambda: logs)
        with enter_session() as sess:
            r.run(run_immediately=True, one_off=True)
            logs.append({
                **logs[0],
                "timestamp_ms": logs[0].get('timestamp_ms') + 2000,
                "event_time": logs[0]['event_time'] + datetime.timedelta(milliseconds=2000),
                "action": "KILL",
            })
            r.run(run_immediately=True, one_off=True)

            res = sess.query(LogLine).all()
            assert len(res) == 2
            assert res[0].type == "TEAM KILL"
            assert res[1].player_1.player_id == first_player_id
            assert res[1].type == "KILL"
            assert res[1].player_2.player_id == second_player_id
