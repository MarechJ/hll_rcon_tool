from datetime import UTC, datetime

from rcon.vip_sync import VipSyncAdd, VipSyncPlan
from rcon.vip_sync_runner import synchronize_gameserver_vips


NOW = datetime(2030, 1, 1, tzinfo=UTC)


def make_plan():
    return VipSyncPlan(
        to_add=(VipSyncAdd("add-1", "Player"),),
        to_remove=frozenset({"remove-1"}),
        unchanged=frozenset({"unchanged-1"}),
        unknown=frozenset(),
    )


class FakeRcon:
    def __init__(self):
        self.calls = []

    def get_vip_ids(self):
        self.calls.append(("get",))
        return [
            {
                "player_id": "unchanged-1",
                "name": "",
                "vip_expiration": None,
            }
        ]

    def add_vip_to_gameserver(self, player_id, description):
        self.calls.append(("add", player_id, description))
        return True

    def remove_vip_from_gameserver(self, player_id):
        self.calls.append(("remove", player_id))
        return True


def test_runner_defaults_to_read_only_dry_run(monkeypatch):
    captured = {}

    def fake_build_plan(gameserver_vips, server_number, timestamp):
        captured["gameserver_vips"] = gameserver_vips
        captured["server_number"] = server_number
        captured["timestamp"] = timestamp
        return make_plan()

    monkeypatch.setattr(
        "rcon.vip_sync_runner.build_database_vip_sync_plan",
        fake_build_plan,
    )

    rcon = FakeRcon()
    result = synchronize_gameserver_vips(
        server_number=2,
        rcon=rcon,
        timestamp=NOW,
    )

    assert result.execution.dry_run is True
    assert result.execution.added == frozenset()
    assert result.execution.removed == frozenset()
    assert rcon.calls == [("get",)]
    assert captured == {
        "gameserver_vips": {"unchanged-1": ""},
        "server_number": 2,
        "timestamp": NOW,
    }


def test_runner_applies_only_when_explicitly_enabled(monkeypatch):
    monkeypatch.setattr(
        "rcon.vip_sync_runner.build_database_vip_sync_plan",
        lambda **kwargs: make_plan(),
    )

    rcon = FakeRcon()
    result = synchronize_gameserver_vips(
        server_number=1,
        rcon=rcon,
        timestamp=NOW,
        dry_run=False,
    )

    assert result.execution.dry_run is False
    assert result.execution.added == frozenset({"add-1"})
    assert result.execution.removed == frozenset({"remove-1"})
    assert rcon.calls == [
        ("get",),
        ("add", "add-1", "Player"),
        ("remove", "remove-1"),
    ]
