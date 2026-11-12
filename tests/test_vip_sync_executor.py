from rcon.vip_sync import VipSyncAdd, VipSyncPlan
from rcon.vip_sync_executor import execute_vip_sync_plan


def make_plan(
    additions=(),
    removals=frozenset(),
):
    return VipSyncPlan(
        to_add=tuple(additions),
        to_remove=frozenset(removals),
        unchanged=frozenset(),
        unknown=frozenset(),
    )


class FakeRcon:
    def __init__(
        self,
        add_results=None,
        remove_results=None,
        add_errors=None,
        remove_errors=None,
    ):
        self.add_results = add_results or {}
        self.remove_results = remove_results or {}
        self.add_errors = add_errors or {}
        self.remove_errors = remove_errors or {}
        self.calls = []

    def add_vip_to_gameserver(self, player_id, description):
        self.calls.append(("add", player_id, description))
        if player_id in self.add_errors:
            raise self.add_errors[player_id]
        return self.add_results.get(player_id, True)

    def remove_vip_from_gameserver(self, player_id):
        self.calls.append(("remove", player_id))
        if player_id in self.remove_errors:
            raise self.remove_errors[player_id]
        return self.remove_results.get(player_id, True)


def test_defaults_to_dry_run_without_rcon_writes():
    plan = make_plan(
        additions=[VipSyncAdd("add-1", "Player")],
        removals={"remove-1"},
    )
    rcon = FakeRcon()

    result = execute_vip_sync_plan(plan, rcon)

    assert result.dry_run is True
    assert result.successful is True
    assert result.added == frozenset()
    assert result.removed == frozenset()
    assert result.skipped_additions == plan.to_add
    assert result.skipped_removals == plan.to_remove
    assert rcon.calls == []


def test_applies_additions_before_removals():
    plan = make_plan(
        additions=[
            VipSyncAdd("add-2", "Second"),
            VipSyncAdd("add-1", "First"),
        ],
        removals={"remove-2", "remove-1"},
    )
    rcon = FakeRcon()

    result = execute_vip_sync_plan(
        plan,
        rcon,
        dry_run=False,
    )

    assert result.successful is True
    assert result.added == frozenset({"add-1", "add-2"})
    assert result.removed == frozenset({"remove-1", "remove-2"})
    assert rcon.calls == [
        ("add", "add-2", "Second"),
        ("add", "add-1", "First"),
        ("remove", "remove-1"),
        ("remove", "remove-2"),
    ]


def test_false_results_are_reported_and_processing_continues():
    plan = make_plan(
        additions=[
            VipSyncAdd("add-fail", "Failure"),
            VipSyncAdd("add-ok", "Success"),
        ],
        removals={"remove-fail", "remove-ok"},
    )
    rcon = FakeRcon(
        add_results={"add-fail": False},
        remove_results={"remove-fail": False},
    )

    result = execute_vip_sync_plan(
        plan,
        rcon,
        dry_run=False,
    )

    assert result.added == frozenset({"add-ok"})
    assert result.removed == frozenset({"remove-ok"})
    assert [(item.action, item.player_id) for item in result.failures] == [
        ("add", "add-fail"),
        ("remove", "remove-fail"),
    ]
    assert result.successful is False


def test_exceptions_are_reported_and_processing_continues():
    plan = make_plan(
        additions=[
            VipSyncAdd("add-error", "Failure"),
            VipSyncAdd("add-ok", "Success"),
        ],
        removals={"remove-error", "remove-ok"},
    )
    rcon = FakeRcon(
        add_errors={"add-error": RuntimeError("add failed")},
        remove_errors={"remove-error": RuntimeError("remove failed")},
    )

    result = execute_vip_sync_plan(
        plan,
        rcon,
        dry_run=False,
    )

    assert result.added == frozenset({"add-ok"})
    assert result.removed == frozenset({"remove-ok"})
    assert [(item.action, item.player_id) for item in result.failures] == [
        ("add", "add-error"),
        ("remove", "remove-error"),
    ]
    assert "RuntimeError: add failed" == result.failures[0].error
    assert "RuntimeError: remove failed" == result.failures[1].error


def test_empty_plan_performs_no_writes():
    rcon = FakeRcon()

    result = execute_vip_sync_plan(
        make_plan(),
        rcon,
        dry_run=False,
    )

    assert result.successful is True
    assert result.added == frozenset()
    assert result.removed == frozenset()
    assert rcon.calls == []
