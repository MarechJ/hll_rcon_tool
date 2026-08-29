from contextlib import nullcontext
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

import rcon.rcon as rcon_module
import rcon.vip as vip_module
import rcon.vip_sync_runner as sync_runner_module
from rcon.rcon import Rcon


def make_sync_result(successful=True):
    return SimpleNamespace(
        execution=SimpleNamespace(successful=successful),
    )


def test_legacy_get_vip_ids_uses_effective_list_expirations(monkeypatch):
    expiration = datetime(2031, 1, 1, tzinfo=UTC)
    parent_class = Rcon.__mro__[1]

    monkeypatch.setattr(
        parent_class,
        "get_vip_ids",
        lambda self: [
            {"player_id": "player-2", "name": "Bravo"},
            {"player_id": "player-1", "name": "Alpha"},
            {"player_id": "unknown", "name": "Charlie"},
        ],
    )
    monkeypatch.setattr(rcon_module, "get_server_number", lambda: 2)
    monkeypatch.setattr(
        rcon_module,
        "enter_session",
        lambda: nullcontext(object()),
    )
    monkeypatch.setattr(
        vip_module,
        "get_effective_vip_records",
        lambda sess, server_number: {
            "player-1": SimpleNamespace(expires_at=expiration),
            "player-2": SimpleNamespace(expires_at=None),
        },
    )

    Rcon.get_vip_ids.cache_clear()
    ctl = object.__new__(Rcon)

    assert ctl.get_vip_ids() == [
        {
            "player_id": "player-1",
            "name": "Alpha",
            "vip_expiration": expiration,
        },
        {
            "player_id": "player-2",
            "name": "Bravo",
            "vip_expiration": None,
        },
        {
            "player_id": "unknown",
            "name": "Charlie",
            "vip_expiration": None,
        },
    ]
    Rcon.get_vip_ids.cache_clear()


@pytest.mark.parametrize(
    ("expiration", "expected"),
    [
        (None, None),
        ("2031-02-03T04:05:06+00:00", datetime(2031, 2, 3, 4, 5, 6, tzinfo=UTC)),
        ("3000-01-01T00:00:00+00:00", None),
        ("not-a-date", None),
    ],
)
def test_legacy_add_vip_writes_default_and_synchronizes(
    monkeypatch,
    expiration,
    expected,
):
    captured = {}

    monkeypatch.setattr(rcon_module, "get_server_number", lambda: 3)

    def fake_upsert(**kwargs):
        captured["upsert"] = kwargs

    def fake_sync(**kwargs):
        captured["sync"] = kwargs
        return make_sync_result()

    monkeypatch.setattr(
        vip_module,
        "upsert_default_vip_record",
        fake_upsert,
    )
    monkeypatch.setattr(
        sync_runner_module,
        "synchronize_gameserver_vips",
        fake_sync,
    )

    ctl = object.__new__(Rcon)

    assert ctl.add_vip(
        player_id="00020000000000000000000000000001",
        description="Legacy API test",
        expiration=expiration,
    )

    assert captured["upsert"] == {
        "player_id": "00020000000000000000000000000001",
        "server_number": 3,
        "description": "Legacy API test",
        "expires_at": expected,
    }
    assert captured["sync"] == {
        "server_number": 3,
        "rcon": ctl,
        "dry_run": False,
    }


def test_legacy_remove_vip_deactivates_default_and_synchronizes(monkeypatch):
    captured = {}

    monkeypatch.setattr(rcon_module, "get_server_number", lambda: 4)

    def fake_deactivate(**kwargs):
        captured["deactivate"] = kwargs
        return True

    def fake_sync(**kwargs):
        captured["sync"] = kwargs
        return make_sync_result()

    monkeypatch.setattr(
        vip_module,
        "deactivate_default_vip_record",
        fake_deactivate,
    )
    monkeypatch.setattr(
        sync_runner_module,
        "synchronize_gameserver_vips",
        fake_sync,
    )

    ctl = object.__new__(Rcon)

    assert ctl.remove_vip("00020000000000000000000000000002")
    assert captured["deactivate"] == {
        "player_id": "00020000000000000000000000000002",
        "server_number": 4,
    }
    assert captured["sync"] == {
        "server_number": 4,
        "rcon": ctl,
        "dry_run": False,
    }


def test_legacy_remove_vip_without_default_record_does_not_touch_server(
    monkeypatch,
):
    monkeypatch.setattr(rcon_module, "get_server_number", lambda: 1)
    monkeypatch.setattr(
        vip_module,
        "deactivate_default_vip_record",
        lambda **kwargs: False,
    )

    def unexpected_sync(**kwargs):
        raise AssertionError("Synchronization must not run")

    monkeypatch.setattr(
        sync_runner_module,
        "synchronize_gameserver_vips",
        unexpected_sync,
    )

    ctl = object.__new__(Rcon)
    assert ctl.remove_vip("00020000000000000000000000000003") is False


def test_legacy_remove_all_vips_only_deactivates_default_list(monkeypatch):
    captured = {}

    monkeypatch.setattr(rcon_module, "get_server_number", lambda: 5)

    def fake_deactivate_all(**kwargs):
        captured["deactivate_all"] = kwargs
        return 3

    def fake_sync(**kwargs):
        captured["sync"] = kwargs
        return make_sync_result()

    monkeypatch.setattr(
        vip_module,
        "deactivate_all_default_vip_records",
        fake_deactivate_all,
    )
    monkeypatch.setattr(
        sync_runner_module,
        "synchronize_gameserver_vips",
        fake_sync,
    )

    ctl = object.__new__(Rcon)

    assert ctl.remove_all_vips()
    assert captured["deactivate_all"] == {"server_number": 5}
    assert captured["sync"] == {
        "server_number": 5,
        "rcon": ctl,
        "dry_run": False,
    }
