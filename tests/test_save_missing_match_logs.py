import os
from contextlib import nullcontext
from datetime import UTC, datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

os.environ.setdefault("HLL_MAINTENANCE_CONTAINER", "1")

from rcon import workers
from rcon.logs.recorder import LogRecorder
from rcon.models import LogLine
from rcon.rcon import Rcon


def make_log(event_time, content="MATCH START UTAH BEACH WARFARE", age="1 sec"):
    raw = f"[{age} ({int(event_time.timestamp())})] {content}"
    return Rcon.parse_logs([raw])["logs"][0]


def database_log(log):
    return LogLine(
        event_time=log["event_time"],
        type=log["action"],
        content=log["message"],
        raw=log["raw"],
        server="1",
    )


@pytest.fixture
def backfill(monkeypatch):
    now = datetime.now(UTC).replace(microsecond=0)
    session = Mock()
    session.get_bind.return_value.dialect.name = "sqlite"
    rcon = Mock()
    rcon.get_structured_logs.return_value = {"logs": []}
    recorder = Mock(spec=LogRecorder)
    database = []
    cache = []
    monkeypatch.setattr(workers, "enter_session", lambda: nullcontext(session))
    monkeypatch.setattr(workers, "get_server_number", lambda: "1")
    monkeypatch.setattr(workers, "_are_match_logs_available", lambda *args: True)
    monkeypatch.setattr(workers, "get_rcon", lambda: rcon)
    monkeypatch.setattr(workers, "LogsHistory", lambda: cache)
    monkeypatch.setattr(
        workers, "get_historical_logs_records", lambda *args, **kwargs: database
    )
    monkeypatch.setattr(workers, "LogRecorder", lambda: recorder)
    return SimpleNamespace(
        now=now,
        session=session,
        rcon=rcon,
        recorder=recorder,
        database=database,
        cache=cache,
        map_info={
            "start": (now - timedelta(hours=2)).timestamp(),
            "end": (now - timedelta(minutes=5)).timestamp(),
        },
    )


def test_saves_only_server_logs_missing_from_database(backfill):
    existing = make_log(backfill.now - timedelta(minutes=90))
    missing = make_log(backfill.now - timedelta(minutes=60))
    database_only = make_log(
        backfill.now - timedelta(minutes=30),
        "MATCH ENDED `UTAH BEACH WARFARE` ALLIED (0 - 5) AXIS",
    )
    outside_match = make_log(backfill.now)
    backfill.database.extend([database_log(existing), database_log(database_only)])
    backfill.rcon.get_structured_logs.return_value["logs"] = [
        outside_match,
        missing,
        existing,
    ]

    workers.save_missing_match_logs(backfill.map_info)

    backfill.recorder._save_logs.assert_called_once_with(backfill.session, [missing])


def test_backfilled_logs_are_accepted_by_real_recorder(backfill, monkeypatch):
    missing = make_log(backfill.now - timedelta(minutes=60))
    backfill.rcon.get_structured_logs.return_value["logs"] = [missing]
    monkeypatch.setenv("SERVER_NUMBER", "1")
    monkeypatch.setattr(workers, "LogRecorder", LogRecorder)

    workers.save_missing_match_logs(backfill.map_info)

    backfill.session.add_all.assert_called_once()
    rows = list(backfill.session.add_all.call_args.args[0])
    assert len(rows) == 1
    assert isinstance(rows[0], LogLine)
    assert rows[0].event_time == missing["event_time"]
    assert rows[0].content == missing["message"]
    backfill.session.flush.assert_called_once()


def test_relative_age_changes_do_not_cause_duplicates(backfill):
    event_time = backfill.now - timedelta(minutes=60)
    cached = make_log(event_time, age="1 sec")
    fetched = make_log(event_time, age="1:00:00 hours")
    assert cached["raw"] != fetched["raw"]
    backfill.database.append(database_log(cached))
    backfill.cache.append(cached)
    backfill.rcon.get_structured_logs.return_value["logs"] = [fetched]

    workers.save_missing_match_logs(backfill.map_info)

    backfill.recorder._save_logs.assert_not_called()


def test_retry_does_not_save_recovered_logs_again(backfill):
    event_time = backfill.now - timedelta(minutes=60)
    missing = make_log(event_time)
    backfill.rcon.get_structured_logs.return_value["logs"] = [missing]
    backfill.recorder._save_logs.side_effect = lambda session, logs: (
        backfill.database.extend(database_log(log) for log in logs)
    )

    workers.save_missing_match_logs(backfill.map_info)
    backfill.rcon.get_structured_logs.return_value["logs"] = [
        make_log(event_time, age="1:00:30 hours")
    ]
    workers.save_missing_match_logs(backfill.map_info)

    backfill.recorder._save_logs.assert_called_once_with(backfill.session, [missing])


@pytest.mark.parametrize("database_timezone", [None, timezone(timedelta(hours=2))])
def test_database_timestamp_representation_does_not_cause_duplicates(
    backfill, database_timezone
):
    log = make_log(backfill.now - timedelta(minutes=60))
    stored = database_log(log)
    stored.event_time = (
        stored.event_time.replace(tzinfo=None)
        if database_timezone is None
        else stored.event_time.astimezone(database_timezone)
    )
    backfill.database.append(stored)
    backfill.rcon.get_structured_logs.return_value["logs"] = [log]

    workers.save_missing_match_logs(backfill.map_info)

    backfill.recorder._save_logs.assert_not_called()


def test_same_message_at_different_times_is_recovered(backfill):
    existing = make_log(backfill.now - timedelta(minutes=90))
    missing = make_log(backfill.now - timedelta(minutes=60))
    assert existing["message"] == missing["message"]
    backfill.database.append(database_log(existing))
    backfill.rcon.get_structured_logs.return_value["logs"] = [missing, existing]

    workers.save_missing_match_logs(backfill.map_info)

    backfill.recorder._save_logs.assert_called_once_with(backfill.session, [missing])


def test_same_message_with_different_action_is_recovered(backfill):
    event_time = backfill.now - timedelta(minutes=60)
    connected = make_log(event_time, "CONNECTED Waxxeer (12345678901234567)")
    disconnected = make_log(event_time, "DISCONNECTED Waxxeer (12345678901234567)")
    assert connected["message"] == disconnected["message"]
    backfill.database.append(database_log(connected))
    backfill.rcon.get_structured_logs.return_value["logs"] = [connected, disconnected]

    workers.save_missing_match_logs(backfill.map_info)

    backfill.recorder._save_logs.assert_called_once_with(
        backfill.session, [disconnected]
    )


def test_duplicate_server_events_are_saved_once(backfill):
    event_time = backfill.now - timedelta(minutes=60)
    first = make_log(event_time, age="1 sec")
    second = make_log(event_time, age="2 sec")
    backfill.rcon.get_structured_logs.return_value["logs"] = [first, second]

    workers.save_missing_match_logs(backfill.map_info)

    saved = backfill.recorder._save_logs.call_args.args[1]
    assert len(saved) == 1
    assert saved[0]["event_time"] == event_time


def test_cache_warning_identifies_server_event_missing_from_cache(
    backfill, monkeypatch
):
    logger = Mock(wraps=workers.logger)
    monkeypatch.setattr(workers, "logger", logger)
    event_time = backfill.now - timedelta(minutes=60)
    existing = make_log(event_time, "CONNECTED Waxxeer (12345678901234567)")
    missing = make_log(event_time, "DISCONNECTED Waxxeer (12345678901234567)")
    backfill.cache.append(existing)
    backfill.rcon.get_structured_logs.return_value["logs"] = [existing, missing]

    workers.save_missing_match_logs(backfill.map_info)

    warnings = [
        call
        for call in logger.warning.call_args_list
        if call.args[0] == "Missing log - CACHE: %s"
    ]
    assert len(warnings) == 1
    assert warnings[0].args[1] == missing


def test_lookback_includes_whole_days(backfill, monkeypatch):
    class FrozenDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return backfill.now

    monkeypatch.setattr(workers.datetime, "datetime", FrozenDatetime)
    backfill.map_info["start"] = (backfill.now - timedelta(hours=25)).timestamp()

    workers.save_missing_match_logs(backfill.map_info)

    backfill.rcon.get_structured_logs.assert_called_once_with(since_min_ago=1501)
