import json
import time
from unittest.mock import MagicMock

from pytest import fixture, raises

from rcon.automods.team_balance import (
    MATCH_WINNERS_KEY,
    TeamBalanceAutomod,
)
from rcon.user_config.auto_mod_team_balance import AutoModTeamBalanceUserConfig


class FakeRedis:
    """Minimal in-memory stand-in for the redis client used by the automod."""

    def __init__(self, initial=None):
        self.store = {}
        if initial is not None:
            self.store[MATCH_WINNERS_KEY] = json.dumps(initial)

    def get(self, key):
        return self.store.get(key)

    def setex(self, key, ttl, value):
        self.store[key] = value


# --------------------------------------------------------------------------- #
# Fixture builders
# --------------------------------------------------------------------------- #
def mk_squad(
    name, team, squad_type, players, combat=0, offense=0, defense=0, support=0, level=0
):
    return (
        name,
        {
            "type": squad_type,
            "has_leader": True,
            "combat": combat,
            "offense": offense,
            "defense": defense,
            "support": support,
            "kills": 0,
            "deaths": 0,
            "players": [
                {
                    "player_id": pid,
                    "name": pid,
                    "team": team,
                    "role": "rifleman",
                    "level": level,
                }
                for pid in players
            ],
        },
    )


def mk_team_view(allies_squads, axis_squads, allies_cmd=None, axis_cmd=None):
    return {
        "allies": {
            "commander": allies_cmd,
            "squads": {name: squad for name, squad in allies_squads},
        },
        "axis": {
            "commander": axis_cmd,
            "squads": {name: squad for name, squad in axis_squads},
        },
    }


def mk_config(**overrides):
    defaults = dict(
        enabled=True,
        dry_run=False,
        skip_when_seeding=False,
        seeding_player_threshold=0,
        min_players_for_balance=0,
        max_players_per_team_delta=2,
        score_gap_threshold=0,
        win_streak_threshold=3,
        fast_match_minutes=30,
        balance_armor=True,
        max_armor_squad_delta=0,
        switch_delay_seconds=0,
    )
    defaults.update(overrides)
    return AutoModTeamBalanceUserConfig(**defaults)


def switched_ids(rcon):
    return [
        call.args[0] if call.args else call.kwargs.get("player_id")
        for call in rcon.switch_player_now.call_args_list
    ]


def run_end(mod, rcon, duration=None, winner_score="ALLIED (5 - 0) AXIS"):
    # Bypass MapsHistory/redis-based duration lookup.
    mod._match_duration_minutes = lambda struct_log: duration
    rcon.switch_player_now.return_value = True
    struct_log = {
        "sub_content": f"`FOY WARFARE` {winner_score}",
        "timestamp_ms": int(time.time() * 1000),
    }
    mod.on_match_end(rcon, struct_log)


# --------------------------------------------------------------------------- #
# Pure helpers
# --------------------------------------------------------------------------- #
def test_parse_winner():
    parse = TeamBalanceAutomod._parse_winner
    assert parse("`FOY WARFARE` ALLIED (5 - 0) AXIS") == "allies"
    assert parse("`FOY WARFARE` ALLIED (1 - 4) AXIS") == "axis"
    assert parse("ALLIED (3 - 3) AXIS") is None
    assert parse("no score here") is None


def test_alternating_streak():
    streak = TeamBalanceAutomod._alternating_streak
    # Same team winning while sides swap -> raw winner alternates.
    assert streak(["allies", "axis", "allies"]) == 3
    # Raw winner repeats -> win passed to the other group, streak breaks.
    assert streak(["allies", "allies", "axis"]) == 1
    assert streak(["axis", "allies", "allies"]) == 2
    assert streak([]) == 0
    assert streak([None, "allies"]) == 0


# --------------------------------------------------------------------------- #
# Steamroll gating
# --------------------------------------------------------------------------- #
def test_long_decisive_win_is_not_a_steamroll():
    """A 60 minute 5-0 must NOT trigger balancing (margin never triggers)."""
    tv = mk_team_view(
        allies_squads=[
            mk_squad("able", "allies", "infantry", ["a1", "a2", "a3", "a4", "a5", "a6"])
        ],
        axis_squads=[mk_squad("baker", "axis", "infantry", ["x1", "x2"])],
    )
    rcon = MagicMock()
    rcon.get_team_view.return_value = tv
    mod = TeamBalanceAutomod(mk_config(win_streak_threshold=3), FakeRedis())
    run_end(mod, rcon, duration=60, winner_score="ALLIED (5 - 0) AXIS")
    rcon.switch_player_now.assert_not_called()


def test_fast_match_triggers():
    tv = mk_team_view(
        allies_squads=[
            mk_squad("able", "allies", "infantry", ["a1", "a2", "a3"]),
            mk_squad("baker", "allies", "infantry", ["a4", "a5", "a6"]),
        ],
        axis_squads=[mk_squad("charlie", "axis", "infantry", ["x1", "x2"])],
    )
    rcon = MagicMock()
    rcon.get_team_view.return_value = tv
    mod = TeamBalanceAutomod(mk_config(), FakeRedis())
    run_end(mod, rcon, duration=10)
    assert len(switched_ids(rcon)) > 0


def test_streak_triggers_without_fast_match():
    tv = mk_team_view(
        allies_squads=[
            mk_squad("able", "allies", "infantry", ["a1", "a2", "a3"]),
            mk_squad("baker", "allies", "infantry", ["a4", "a5", "a6"]),
        ],
        axis_squads=[mk_squad("charlie", "axis", "infantry", ["x1", "x2"])],
    )
    rcon = MagicMock()
    rcon.get_team_view.return_value = tv
    # Prior winners (newest-first) axis, allies; current match allies -> [allies, axis, allies].
    mod = TeamBalanceAutomod(
        mk_config(win_streak_threshold=3), FakeRedis(initial=["axis", "allies"])
    )
    run_end(mod, rcon, duration=90, winner_score="ALLIED (5 - 0) AXIS")
    assert len(switched_ids(rcon)) > 0


def test_stale_match_end_ignored():
    """A match-end event older than the freshness window (e.g. old logs re-read
    after a restart) must be ignored entirely: no rebalance, no team-view fetch,
    and no winner recorded, even if it would otherwise be a steamroll."""
    tv = mk_team_view(
        allies_squads=[
            mk_squad("able", "allies", "infantry", ["a1", "a2", "a3"]),
            mk_squad("baker", "allies", "infantry", ["a4", "a5", "a6"]),
        ],
        axis_squads=[mk_squad("charlie", "axis", "infantry", ["x1", "x2"])],
    )
    rcon = MagicMock()
    rcon.get_team_view.return_value = tv
    fake = FakeRedis()
    mod = TeamBalanceAutomod(mk_config(), fake)
    mod._match_duration_minutes = lambda struct_log: 5  # a fast match, would trigger
    struct_log = {
        "sub_content": "`FOY WARFARE` ALLIED (5 - 0) AXIS",
        "timestamp_ms": int((time.time() - 1800) * 1000),  # ended 30 min ago
    }
    mod.on_match_end(rcon, struct_log)
    rcon.switch_player_now.assert_not_called()
    rcon.get_team_view.assert_not_called()
    assert fake.get(MATCH_WINNERS_KEY) is None


# --------------------------------------------------------------------------- #
# Average level balance
# --------------------------------------------------------------------------- #
def _stacked_team_view():
    """Equal headcount, but allies are all level 400 and axis all level 10."""
    return mk_team_view(
        allies_squads=[
            mk_squad("able", "allies", "infantry", ["a1", "a2", "a3"], level=400),
            mk_squad("baker", "allies", "infantry", ["a4", "a5", "a6"], level=400),
        ],
        axis_squads=[
            mk_squad("charlie", "axis", "infantry", ["x1", "x2", "x3"], level=10),
            mk_squad("dog", "axis", "infantry", ["x4", "x5", "x6"], level=10),
        ],
    )


def test_level_gap_triggers_and_swaps_without_steamroll():
    rcon = MagicMock()
    rcon.get_team_view.return_value = _stacked_team_view()
    mod = TeamBalanceAutomod(
        mk_config(
            balance_by_level=True, level_gap_threshold=50, win_streak_threshold=3
        ),
        FakeRedis(),
    )
    # Not a fast match and no streak: only the level gap can trigger.
    run_end(mod, rcon, duration=90, winner_score="ALLIED (5 - 0) AXIS")

    switched = switched_ids(rcon)
    moved_allies = [p for p in switched if p.startswith("a")]
    moved_axis = [p for p in switched if p.startswith("x")]
    # A swap moved a high-level allies squad out and a low-level axis squad in.
    assert moved_allies and moved_axis
    # Headcount preserved: the same number crossed each way.
    assert len(moved_allies) == len(moved_axis)


def test_level_balance_off_by_default_does_nothing():
    rcon = MagicMock()
    rcon.get_team_view.return_value = _stacked_team_view()
    # balance_by_level defaults to False; long match, no streak -> no trigger.
    mod = TeamBalanceAutomod(mk_config(win_streak_threshold=3), FakeRedis())
    run_end(mod, rcon, duration=90)
    rcon.switch_player_now.assert_not_called()


def test_level_gap_below_threshold_no_swap():
    rcon = MagicMock()
    rcon.get_team_view.return_value = mk_team_view(
        allies_squads=[
            mk_squad("able", "allies", "infantry", ["a1", "a2", "a3"], level=60),
            mk_squad("baker", "allies", "infantry", ["a4", "a5", "a6"], level=60),
        ],
        axis_squads=[
            mk_squad("charlie", "axis", "infantry", ["x1", "x2", "x3"], level=50),
            mk_squad("dog", "axis", "infantry", ["x4", "x5", "x6"], level=50),
        ],
    )
    mod = TeamBalanceAutomod(
        mk_config(
            balance_by_level=True, level_gap_threshold=50, win_streak_threshold=3
        ),
        FakeRedis(),
    )
    # Gap is 10 (< 50), not a fast match, no streak -> no trigger.
    run_end(mod, rcon, duration=90)
    rcon.switch_player_now.assert_not_called()


# --------------------------------------------------------------------------- #
# Guards
# --------------------------------------------------------------------------- #
def test_seeding_guard_skips():
    tv = mk_team_view(
        allies_squads=[
            mk_squad("able", "allies", "infantry", ["a1", "a2", "a3", "a4"])
        ],
        axis_squads=[mk_squad("baker", "axis", "infantry", ["x1"])],
    )
    rcon = MagicMock()
    rcon.get_team_view.return_value = tv
    mod = TeamBalanceAutomod(
        mk_config(skip_when_seeding=True, seeding_player_threshold=50), FakeRedis()
    )
    run_end(mod, rcon, duration=5)
    rcon.switch_player_now.assert_not_called()


def test_min_players_floor_skips():
    tv = mk_team_view(
        allies_squads=[
            mk_squad("able", "allies", "infantry", ["a1", "a2", "a3", "a4"])
        ],
        axis_squads=[mk_squad("baker", "axis", "infantry", ["x1"])],
    )
    rcon = MagicMock()
    rcon.get_team_view.return_value = tv
    mod = TeamBalanceAutomod(mk_config(min_players_for_balance=90), FakeRedis())
    run_end(mod, rcon, duration=5)
    rcon.switch_player_now.assert_not_called()


# --------------------------------------------------------------------------- #
# Armor category (evaluated separately)
# --------------------------------------------------------------------------- #
def test_armor_disparity_moves_one_squad():
    """2 armor squads vs 0 -> exactly one armor squad is moved to equalize."""
    tv = mk_team_view(
        allies_squads=[
            mk_squad("able", "allies", "armor", ["ta1", "ta2"], combat=100),
            mk_squad("baker", "allies", "armor", ["tb1", "tb2"], combat=50),
            # Balanced infantry so Pass 2 does nothing.
            mk_squad("charlie", "allies", "infantry", ["a1", "a2", "a3"]),
        ],
        axis_squads=[mk_squad("dog", "axis", "infantry", ["x1", "x2", "x3"])],
    )
    rcon = MagicMock()
    rcon.get_team_view.return_value = tv
    mod = TeamBalanceAutomod(
        mk_config(balance_armor=True, max_armor_squad_delta=0), FakeRedis()
    )
    run_end(mod, rcon, duration=10)
    moved = switched_ids(rcon)
    # Highest-scoring armor squad (able: ta1, ta2) is moved; exactly one armor squad.
    assert set(moved) == {"ta1", "ta2"}


def test_armor_odd_difference_1v0_does_not_move():
    """1 armor vs 0 at delta 0: moving would just flip to 0-vs-1 (pointless) -> no move."""
    tv = mk_team_view(
        allies_squads=[
            mk_squad("able", "allies", "armor", ["ta1", "ta2"], combat=100),
            mk_squad("charlie", "allies", "infantry", ["a1", "a2", "a3"]),
        ],
        axis_squads=[mk_squad("dog", "axis", "infantry", ["x1", "x2", "x3"])],
    )
    rcon = MagicMock()
    rcon.get_team_view.return_value = tv
    mod = TeamBalanceAutomod(
        mk_config(balance_armor=True, max_armor_squad_delta=0), FakeRedis()
    )
    run_end(mod, rcon, duration=10)
    rcon.switch_player_now.assert_not_called()


def test_armor_odd_difference_3v0_moves_one():
    """3 armor vs 0 at delta 0: one move lands at 1-vs-2 (|gap|=1); a second move is
    over-moving. Exactly one (highest-scoring) armor squad is moved."""
    tv = mk_team_view(
        allies_squads=[
            mk_squad("able", "allies", "armor", ["a1a", "a1b"], combat=300),
            mk_squad("baker", "allies", "armor", ["a2a", "a2b"], combat=200),
            mk_squad("charlie", "allies", "armor", ["a3a", "a3b"], combat=100),
            mk_squad("dog", "allies", "infantry", ["i1", "i2", "i3"]),
        ],
        axis_squads=[mk_squad("easy", "axis", "infantry", ["x1", "x2", "x3"])],
    )
    rcon = MagicMock()
    rcon.get_team_view.return_value = tv
    mod = TeamBalanceAutomod(
        mk_config(balance_armor=True, max_armor_squad_delta=0), FakeRedis()
    )
    run_end(mod, rcon, duration=10)
    # Only the single highest-scoring armor squad (able) moves.
    assert set(switched_ids(rcon)) == {"a1a", "a1b"}


def test_armor_score_trigger_moves_when_counts_within_delta():
    """Counts within delta (2 vs 0, delta=2 -> no count trigger) but the armor score gap
    (600 > threshold 100) triggers a move; one armor squad is moved to close the gap."""
    tv = mk_team_view(
        allies_squads=[
            mk_squad("able", "allies", "armor", ["a1a", "a1b"], combat=300),
            mk_squad("baker", "allies", "armor", ["a2a", "a2b"], combat=300),
            mk_squad("charlie", "allies", "infantry", ["i1", "i2", "i3"]),
        ],
        axis_squads=[mk_squad("dog", "axis", "infantry", ["x1", "x2", "x3"])],
    )
    rcon = MagicMock()
    rcon.get_team_view.return_value = tv
    mod = TeamBalanceAutomod(
        mk_config(
            balance_armor=True, max_armor_squad_delta=2, armor_score_gap_threshold=100
        ),
        FakeRedis(),
    )
    run_end(mod, rcon, duration=10)
    moved = switched_ids(rcon)
    # Exactly one armor squad (2 players) moved; equalizes armor score to 300 vs 300.
    assert len(moved) == 2 and set(moved) <= {"a1a", "a1b", "a2a", "a2b"}


def test_recon_and_commander_never_moved():
    commander = {
        "player_id": "cmd1",
        "name": "cmd1",
        "team": "allies",
        "role": "armycommander",
    }
    tv = mk_team_view(
        allies_squads=[
            mk_squad("able", "allies", "infantry", ["a1", "a2", "a3"]),
            mk_squad("baker", "allies", "infantry", ["a4", "a5", "a6"]),
            mk_squad("recon", "allies", "recon", ["r1", "r2"]),
        ],
        axis_squads=[mk_squad("dog", "axis", "infantry", ["x1"])],
        allies_cmd=commander,
    )
    rcon = MagicMock()
    rcon.get_team_view.return_value = tv
    mod = TeamBalanceAutomod(mk_config(exclude_recon=True), FakeRedis())
    run_end(mod, rcon, duration=10)
    moved = set(switched_ids(rcon))
    assert "cmd1" not in moved
    assert "r1" not in moved and "r2" not in moved


# --------------------------------------------------------------------------- #
# Infantry minimum-squads selection
# --------------------------------------------------------------------------- #
def test_minimum_infantry_squads_selection():
    """allies 9 (6+3) vs axis 3 -> move the 3-man squad only (fewest squads)."""
    tv = mk_team_view(
        allies_squads=[
            mk_squad(
                "able", "allies", "infantry", ["a1", "a2", "a3", "a4", "a5", "a6"]
            ),
            mk_squad("baker", "allies", "infantry", ["b1", "b2", "b3"]),
        ],
        axis_squads=[mk_squad("charlie", "axis", "infantry", ["x1", "x2", "x3"])],
    )
    rcon = MagicMock()
    rcon.get_team_view.return_value = tv
    mod = TeamBalanceAutomod(
        mk_config(balance_armor=False, max_players_per_team_delta=2), FakeRedis()
    )
    run_end(mod, rcon, duration=10)
    moved = set(switched_ids(rcon))
    # Moving baker (3) balances 6v6; able (6) must not move.
    assert moved == {"b1", "b2", "b3"}


def test_already_balanced_no_move():
    tv = mk_team_view(
        allies_squads=[mk_squad("able", "allies", "infantry", ["a1", "a2", "a3"])],
        axis_squads=[mk_squad("charlie", "axis", "infantry", ["x1", "x2", "x3"])],
    )
    rcon = MagicMock()
    rcon.get_team_view.return_value = tv
    mod = TeamBalanceAutomod(mk_config(balance_armor=False), FakeRedis())
    run_end(mod, rcon, duration=10)
    rcon.switch_player_now.assert_not_called()


def test_dry_run_does_not_switch():
    tv = mk_team_view(
        allies_squads=[
            mk_squad("able", "allies", "infantry", ["a1", "a2", "a3"]),
            mk_squad("baker", "allies", "infantry", ["a4", "a5", "a6"]),
        ],
        axis_squads=[mk_squad("charlie", "axis", "infantry", ["x1", "x2"])],
    )
    rcon = MagicMock()
    rcon.get_team_view.return_value = tv
    mod = TeamBalanceAutomod(mk_config(dry_run=True), FakeRedis())
    run_end(mod, rcon, duration=10)
    rcon.switch_player_now.assert_not_called()
    rcon.message_player.assert_not_called()


def test_redis_client_is_required():
    with raises(ValueError, match="requires a Redis client"):
        TeamBalanceAutomod(mk_config(), None)


def test_switch_capacity_is_rechecked_before_each_squad(monkeypatch):
    mod = TeamBalanceAutomod(mk_config(), FakeRedis())
    rcon = MagicMock()
    moves = [
        {
            "team": "allies",
            "type": "infantry",
            "name": "able",
            "size": 2,
            "player_ids": ["a1", "a2"],
            "player_names": ["a1", "a2"],
        }
    ]
    monkeypatch.setattr(
        "rcon.automods.team_balance.get_team_count",
        lambda _team_view, team: 50 if team == "axis" else 0,
    )

    mod._switch_players(rcon, moves, "test")

    rcon.switch_player_now.assert_not_called()


def test_level_swap_does_not_exceed_team_capacity():
    mod = TeamBalanceAutomod(
        mk_config(balance_by_level=True, level_gap_threshold=0), FakeRedis()
    )
    squads = {
        "allies": [
            {
                "type": "infantry",
                "size": 2,
                "level_sum": 200,
                "player_ids": ["a1", "a2"],
            }
        ],
        "axis": [
            {
                "type": "infantry",
                "size": 1,
                "level_sum": 0,
                "player_ids": ["x1"],
            }
        ],
    }

    swaps = mod._select_level_swaps(squads, 50, 49, [], None)

    assert swaps == []


def test_players_are_notified_before_a_delayed_switch(monkeypatch):
    mod = TeamBalanceAutomod(mk_config(switch_delay_seconds=20), FakeRedis())
    rcon = MagicMock()
    moves = [
        {
            "team": "allies",
            "type": "infantry",
            "name": "able",
            "size": 1,
            "player_ids": ["a1"],
            "player_names": ["a1"],
        }
    ]
    timer = MagicMock()
    monkeypatch.setattr("rcon.automods.team_balance.Timer", timer)

    mod._execute(rcon, moves)

    rcon.message_player.assert_called_once()
    rcon.switch_player_now.assert_not_called()
    timer.assert_called_once()
    assert timer.return_value.daemon is True
    timer.return_value.start.assert_called_once()
