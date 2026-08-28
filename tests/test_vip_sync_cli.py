import json
from types import SimpleNamespace

from click.testing import CliRunner

import rcon.cli as cli_module
from rcon.vip_sync import VipSyncAdd
from rcon.vip_sync_executor import VipSyncFailure


def make_result(
    *,
    dry_run,
    failures=(),
):
    addition = VipSyncAdd(
        player_id="00020000000000000000000000000001",
        description="CLI Test",
    )

    return SimpleNamespace(
        plan=SimpleNamespace(
            to_add=(addition,),
            to_remove=frozenset({"00020000000000000000000000000002"}),
        ),
        execution=SimpleNamespace(
            dry_run=dry_run,
            added=(frozenset() if dry_run else frozenset({addition.player_id})),
            removed=(
                frozenset()
                if dry_run
                else frozenset({"00020000000000000000000000000002"})
            ),
            skipped_additions=(addition,) if dry_run else (),
            skipped_removals=(
                frozenset({"00020000000000000000000000000002"})
                if dry_run
                else frozenset()
            ),
            failures=failures,
            successful=not failures,
        ),
    )


def test_vip_list_sync_defaults_to_dry_run(monkeypatch):
    calls = []

    def fake_sync(**kwargs):
        calls.append(kwargs)
        return make_result(dry_run=True)

    monkeypatch.setattr(
        cli_module,
        "synchronize_gameserver_vips",
        fake_sync,
    )
    monkeypatch.setenv("SERVER_NUMBER", "3")

    result = CliRunner().invoke(
        cli_module.cli,
        ["vip-list-sync"],
    )

    assert result.exit_code == 0
    assert calls == [{"server_number": 3, "dry_run": True}]

    payload = json.loads(result.output)
    assert payload["server_number"] == 3
    assert payload["dry_run"] is True
    assert payload["planned_additions"] == 1
    assert payload["planned_removals"] == 1
    assert payload["added"] == []
    assert payload["removed"] == []
    assert payload["skipped_additions"] == 1
    assert payload["skipped_removals"] == 1
    assert payload["failures"] == []


def test_vip_list_sync_requires_apply_for_writes(monkeypatch):
    calls = []

    def fake_sync(**kwargs):
        calls.append(kwargs)
        return make_result(dry_run=False)

    monkeypatch.setattr(
        cli_module,
        "synchronize_gameserver_vips",
        fake_sync,
    )

    result = CliRunner().invoke(
        cli_module.cli,
        [
            "vip-list-sync",
            "--apply",
            "--server-number",
            "2",
        ],
    )

    assert result.exit_code == 0
    assert calls == [{"server_number": 2, "dry_run": False}]

    payload = json.loads(result.output)
    assert payload["server_number"] == 2
    assert payload["dry_run"] is False
    assert payload["added"] == ["00020000000000000000000000000001"]
    assert payload["removed"] == ["00020000000000000000000000000002"]


def test_vip_list_sync_fails_if_an_action_failed(monkeypatch):
    failure = VipSyncFailure(
        action="remove",
        player_id="00020000000000000000000000000002",
        error="Gameserver returned False",
    )

    monkeypatch.setattr(
        cli_module,
        "synchronize_gameserver_vips",
        lambda **kwargs: make_result(
            dry_run=False,
            failures=(failure,),
        ),
    )

    result = CliRunner().invoke(
        cli_module.cli,
        [
            "vip-list-sync",
            "--apply",
            "--server-number",
            "1",
        ],
    )

    assert result.exit_code != 0
    assert '"failures":' in result.output
    assert "completed with 1 failure(s)" in result.output


def test_vip_list_sync_rejects_invalid_server_number():
    result = CliRunner().invoke(
        cli_module.cli,
        [
            "vip-list-sync",
            "--server-number",
            "33",
        ],
    )

    assert result.exit_code != 0
    assert "33 is not in the range 1<=x<=32" in result.output
