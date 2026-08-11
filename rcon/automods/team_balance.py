"""Team-balance automod.

At the end of a match, if the match was a *steamroll*, move whole squads between
teams to rebalance them. Armor squads are balanced as their own category; infantry
squads are balanced by headcount and combat-effectiveness score.

A steamroll is defined by match DURATION (fast matches) or repeated same-team wins
(swap aware), NEVER by score margin. A long decisive win (e.g. a 60 minute 5-0) is
a grind, not a steamroll.
"""

import json
import logging
import re
import time
from itertools import combinations
from threading import Timer
from typing import Literal, Optional

import redis

from rcon.automods.get_team_count import get_team_count
from rcon.discord import send_to_discord_audit
from rcon.user_config.auto_mod_team_balance import AutoModTeamBalanceUserConfig
from rcon.utils import MapsHistory

AUTOMOD_USERNAME = "AutoMod_TeamBalance"
MATCH_WINNERS_KEY = "team_balance:match_winners"
MATCH_WINNERS_TTL = 14 * 24 * 60 * 60  # 14 days
MATCH_WINNERS_MAX = 30
# Ignore match-end events older than this. The log loop re-reads recent logs on startup
# (deduplicated in redis); this is a safety net so a re-read old match never rebalances
# the current teams or corrupts the win streak if that dedup is ever unavailable.
MATCH_END_MAX_AGE_SECONDS = 10 * 60
MAX_TEAM_PLAYERS = 50  # HLL per-team cap

# Squad types (from Rcon._guess_squad_type) excluded from infantry balancing.
# Armor is excluded here because it is handled by the dedicated armor-balancing pass.
_INFANTRY_EXCLUDED_TYPES = {"commander", "artillery", "armor"}

_SCORE_RE = re.compile(r"ALLIED\s*\(\s*(\d+)\s*-\s*(\d+)\s*\)\s*AXIS", re.IGNORECASE)


class TeamBalanceAutomod:
    """Imported from rcon/automods/automod.py, triggered on match end."""

    logger: logging.Logger
    red: redis.StrictRedis
    config: AutoModTeamBalanceUserConfig

    def __init__(self, config: AutoModTeamBalanceUserConfig, red: redis.StrictRedis):
        if red is None:
            raise ValueError("Team balance automod requires a Redis client")
        self.logger = logging.getLogger(__name__)
        self.red = red
        self.config = config

    # ------------------------------------------------------------------ #
    # Entry point
    # ------------------------------------------------------------------ #
    def on_match_end(self, rcon, struct_log) -> None:
        config = self.config

        # Ignore stale match-end events (e.g. old logs re-read after a restart) so we
        # never record a duplicate winner or rebalance based on a match that is long over.
        end_ms = struct_log.get("timestamp_ms")
        if end_ms and time.time() - end_ms / 1000 > MATCH_END_MAX_AGE_SECONDS:
            self.logger.info("Team balance: ignoring stale match-end event")
            return

        # 1. Winner + streak history (recorded every match, even if we don't act)
        winner = self._parse_winner(struct_log.get("sub_content", "") or "")
        winners = self._record_and_get_winners(winner)

        # 2. Match duration (the "fast match" steamroll signal)
        duration_minutes = self._match_duration_minutes(struct_log)

        # 3. Population
        try:
            team_view = rcon.get_team_view()
        except Exception:
            self.logger.exception("Team balance: could not get team view")
            return
        count_allies = get_team_count(team_view, "allies")
        count_axis = get_team_count(team_view, "axis")
        total_players = count_allies + count_axis

        # 4. Seeding guard
        if (
            config.skip_when_seeding
            and total_players <= config.seeding_player_threshold
        ):
            self.logger.info(
                "Team balance: %s players <= seeding threshold %s, skipping",
                total_players,
                config.seeding_player_threshold,
            )
            return

        # 5. Minimum players floor
        if total_players < config.min_players_for_balance:
            self.logger.info(
                "Team balance: %s players < min %s, skipping",
                total_players,
                config.min_players_for_balance,
            )
            return

        # 6. Collect + categorize squads (needed for the level gap and balancing)
        squads = {
            "allies": self._collect_squads(team_view, "allies"),
            "axis": self._collect_squads(team_view, "axis"),
        }

        # 7. Trigger gate. Steamroll = short DURATION or a swap-aware win streak
        #    (margin never triggers). When 'balance by level' is enabled, a large
        #    average player-level gap is an additional trigger.
        is_fast = (
            duration_minutes is not None
            and duration_minutes < config.fast_match_minutes
        )
        streak = self._alternating_streak(winners)
        is_streak = (
            config.win_streak_threshold > 0 and streak >= config.win_streak_threshold
        )

        avg_levels = self._team_average_levels(squads)
        level_gap = abs(avg_levels["allies"] - avg_levels["axis"])
        is_level_stacked = (
            config.balance_by_level and level_gap > config.level_gap_threshold
        )

        if not (is_fast or is_streak or is_level_stacked):
            self.logger.info(
                "Team balance: no trigger (duration=%s min, streak=%s, level_gap=%.0f), "
                "skipping",
                round(duration_minutes, 1) if duration_minutes is not None else None,
                streak,
                level_gap,
            )
            return

        self.logger.info(
            "Team balance: triggered (fast=%s, streak=%s/%s, level_gap=%.0f/%s) - "
            "evaluating",
            is_fast,
            streak,
            config.win_streak_threshold,
            level_gap,
            config.level_gap_threshold if config.balance_by_level else "off",
        )

        cap = config.max_players_to_switch if config.max_players_to_switch > 0 else None
        moves: list[dict] = []

        # 8. Pass 1 - armor balance (separate category)
        if config.balance_armor:
            armor_moves = self._select_armor_moves(
                squads, {"allies": count_allies, "axis": count_axis}, cap
            )
            moves.extend(armor_moves)

        moved_so_far = sum(s["size"] for s in moves)
        cap_remaining = None if cap is None else max(0, cap - moved_so_far)

        # 9. Pass 2 - infantry + headcount balance (accounting for armor moves)
        infantry_moves = self._select_infantry_moves(
            squads,
            count_allies,
            count_axis,
            moves,
            cap_remaining,
        )
        moves.extend(infantry_moves)

        # 10. Pass 3 - average level balance via headcount-preserving squad swaps
        if config.balance_by_level:
            moved_so_far = sum(s["size"] for s in moves)
            level_cap = None if cap is None else max(0, cap - moved_so_far)
            level_swaps = self._select_level_swaps(
                squads, count_allies, count_axis, moves, level_cap
            )
            moves.extend(level_swaps)

        if not moves:
            self.logger.info("Team balance: already balanced, nothing to move")
            return

        # 11. Execute
        self._execute(rcon, moves)

    # ------------------------------------------------------------------ #
    # Steamroll detection helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _parse_winner(sub_content: str) -> Optional[Literal["allies", "axis"]]:
        """Parse the winner from a MATCH ENDED sub_content, e.g.
        '`UTAH BEACH OFFENSIVE` ALLIED (1 - 4) AXIS'. Margin is NOT used to trigger.
        """
        match = _SCORE_RE.search(sub_content)
        if not match:
            return None
        allied, axis = int(match.group(1)), int(match.group(2))
        if allied > axis:
            return "allies"
        if axis > allied:
            return "axis"
        return None

    def _record_and_get_winners(self, winner: Optional[str]) -> list[Optional[str]]:
        """Persist the winner (newest first) and return recent winners."""
        winners: list[Optional[str]] = []
        try:
            raw = self.red.get(MATCH_WINNERS_KEY)
            if raw:
                winners = json.loads(raw)
                if not isinstance(winners, list):
                    winners = []
        except Exception:
            self.logger.exception("Team balance: could not read match history")
            winners = []

        winners.insert(0, winner)
        winners = winners[:MATCH_WINNERS_MAX]

        try:
            self.red.setex(MATCH_WINNERS_KEY, MATCH_WINNERS_TTL, json.dumps(winners))
        except Exception:
            self.logger.exception("Team balance: could not save match history")

        return winners

    @staticmethod
    def _alternating_streak(winners_newest_first: list[Optional[str]]) -> int:
        """Length of the alternating run of raw winners from the most recent match.

        Because teams swap sides every match, the SAME group winning repeatedly shows
        up as the raw winner (allies/axis) ALTERNATING. A repeated raw winner means the
        win passed to the other group, which breaks the streak.
        """
        streak = 0
        prev: Optional[str] = None
        for winner in winners_newest_first:
            if winner is None:
                break
            if prev is None:
                streak = 1
            elif winner != prev:
                streak += 1
            else:
                break
            prev = winner
        return streak

    @staticmethod
    def _match_duration_minutes(struct_log) -> Optional[float]:
        """Duration of the just-ended match, in minutes (None if unknown)."""
        end_ms = struct_log.get("timestamp_ms")
        if not end_ms:
            return None
        end_s = end_ms / 1000
        maps_history = MapsHistory()
        if not maps_history:
            return None
        start_s = maps_history[0].get("start")
        if not start_s or end_s <= start_s:
            return None
        return (end_s - start_s) / 60

    # ------------------------------------------------------------------ #
    # Squad collection / scoring
    # ------------------------------------------------------------------ #
    def _squad_score(self, squad: dict) -> float:
        c = self.config
        return (
            c.weight_combat * squad.get("combat", 0)
            + c.weight_offense * squad.get("offense", 0)
            + c.weight_defense * squad.get("defense", 0)
            + c.weight_support * squad.get("support", 0)
        )

    @staticmethod
    def _team_average_levels(squads: dict) -> dict:
        """Average player level per team, from the collected (non-commander) squads."""
        avg = {}
        for team in ("allies", "axis"):
            players = sum(s["size"] for s in squads[team])
            total = sum(s["level_sum"] for s in squads[team])
            avg[team] = total / players if players else 0.0
        return avg

    def _collect_squads(self, team_view, team: str) -> list[dict]:
        squads = []
        team_data = team_view.get(team) or {}
        for name, squad in (team_data.get("squads") or {}).items():
            players = squad.get("players") or []
            # Keep ids and names aligned by pairing them from the same filtered set.
            kept = [
                (p.get("player_id"), p.get("name"), int(p.get("level") or 0))
                for p in players
                if p.get("player_id")
            ]
            if not kept:
                continue
            squads.append(
                {
                    "team": team,
                    "name": name,
                    "type": squad.get("type"),
                    "size": len(kept),
                    "score": self._squad_score(squad),
                    "level_sum": sum(lvl for _, _, lvl in kept),
                    "player_ids": [pid for pid, _, _ in kept],
                    "player_names": [pname for _, pname, _ in kept],
                }
            )
        return squads

    def _is_movable_infantry(self, squad: dict) -> bool:
        stype = squad.get("type")
        if stype in _INFANTRY_EXCLUDED_TYPES:
            return False
        if stype == "recon" and self.config.exclude_recon:
            return False
        return True

    # ------------------------------------------------------------------ #
    # Pass 1 - armor balance
    # ------------------------------------------------------------------ #
    def _select_armor_moves(
        self, squads: dict, team_counts: dict, cap: Optional[int]
    ) -> list[dict]:
        armor = {
            team: [s for s in squads[team] if s.get("type") == "armor"]
            for team in ("allies", "axis")
        }
        counts = {team: len(armor[team]) for team in ("allies", "axis")}
        scores = {
            team: sum(s["score"] for s in armor[team]) for team in ("allies", "axis")
        }

        delta = self.config.max_armor_squad_delta
        threshold = self.config.armor_score_gap_threshold

        count_diff = abs(counts["allies"] - counts["axis"])
        score_gap = abs(scores["allies"] - scores["axis"])

        count_trigger = count_diff > delta
        score_trigger = threshold > 0 and score_gap > threshold
        if not (count_trigger or score_trigger):
            return []

        # Move armor FROM the team with more armor squads (count driven), or from the
        # higher-scoring armor team when only the score gap is out of tolerance.
        if count_trigger:
            source = "allies" if counts["allies"] > counts["axis"] else "axis"
        else:
            source = "allies" if scores["allies"] >= scores["axis"] else "axis"
        dest = "axis" if source == "allies" else "allies"

        return self._best_armor_subset(
            armor[source],
            counts[source],
            counts[dest],
            scores[source],
            scores[dest],
            team_counts.get(dest, 0),
            delta,
            threshold,
            cap,
        )

    def _best_armor_subset(
        self,
        source_armor: list[dict],
        source_count: int,
        dest_count: int,
        source_score: float,
        dest_score: float,
        dest_player_total: int,
        delta: int,
        threshold: float,
        cap: Optional[int],
    ) -> list[dict]:
        """Fewest armor squads that keep the armor squad COUNT within `delta` and get the
        armor score gap as low as possible (within `threshold` when achievable). A team
        has at most a handful of armor squads, so we can enumerate subsets."""
        n = len(source_armor)
        count_diff_before = abs(source_count - dest_count)
        feasible: list[tuple] = []
        improving: list[tuple] = []

        for k in range(0, n + 1):
            for combo in combinations(range(n), k):
                chosen = [source_armor[i] for i in combo]
                moved_players = sum(s["size"] for s in chosen)
                if cap is not None and moved_players > cap:
                    continue
                if dest_player_total + moved_players > MAX_TEAM_PLAYERS:
                    continue
                new_count_diff = abs((source_count - k) - (dest_count + k))
                moved_score = sum(s["score"] for s in chosen)
                new_score_gap = abs(
                    (source_score - moved_score) - (dest_score + moved_score)
                )
                if new_count_diff <= delta:
                    feasible.append((k, new_score_gap, chosen))
                elif new_count_diff < count_diff_before:
                    improving.append((new_count_diff, k, new_score_gap, chosen))

        if feasible:
            min_gap = min(item[1] for item in feasible)
            acceptable_gap = max(threshold, min_gap)
            candidates = [item for item in feasible if item[1] <= acceptable_gap + 1e-9]
            candidates.sort(key=lambda item: (item[0], item[1]))
            return candidates[0][2]

        if improving:
            improving.sort(key=lambda item: (item[0], item[1], item[2]))
            return improving[0][3]

        return []

    # ------------------------------------------------------------------ #
    # Pass 2 - infantry + headcount balance
    # ------------------------------------------------------------------ #
    def _select_infantry_moves(
        self,
        squads: dict,
        count_allies: int,
        count_axis: int,
        prior_moves: list[dict],
        cap_remaining: Optional[int],
    ) -> list[dict]:
        # Apply the headcount effect of Pass 1 armor moves.
        totals = {"allies": count_allies, "axis": count_axis}
        for move in prior_moves:
            src = move["team"]
            dst = "axis" if src == "allies" else "allies"
            totals[src] -= move["size"]
            totals[dst] += move["size"]

        moved_ids = {pid for m in prior_moves for pid in m["player_ids"]}

        infantry = {}
        inf_score = {}
        for team in ("allies", "axis"):
            elig = [
                s
                for s in squads[team]
                if self._is_movable_infantry(s)
                and not any(pid in moved_ids for pid in s["player_ids"])
            ]
            infantry[team] = elig
            inf_score[team] = sum(s["score"] for s in elig)

        delta = self.config.max_players_per_team_delta
        threshold = self.config.score_gap_threshold

        # Decide the source team: prefer reducing a headcount imbalance, otherwise
        # reduce the infantry score gap by moving from the higher-scoring team.
        if abs(totals["allies"] - totals["axis"]) > delta:
            source = "allies" if totals["allies"] > totals["axis"] else "axis"
        else:
            source = "allies" if inf_score["allies"] >= inf_score["axis"] else "axis"
        dest = "axis" if source == "allies" else "allies"

        return self._best_subset(
            infantry[source],
            totals[source],
            totals[dest],
            inf_score[source],
            inf_score[dest],
            delta,
            threshold,
            cap_remaining,
        )

    def _best_subset(
        self,
        source_squads: list[dict],
        source_total: int,
        dest_total: int,
        source_score: float,
        dest_score: float,
        delta: int,
        threshold: float,
        cap_remaining: Optional[int],
    ) -> list[dict]:
        """Fewest squads that keep headcount within delta and get the score gap as low
        as possible (within threshold when achievable). Enumerates subsets (HLL caps a
        team at 6 squads, so this stays tiny).
        """
        n = len(source_squads)
        diff_before = abs(source_total - dest_total)

        feasible: list[tuple] = []  # (num_squads, score_gap, subset)
        improving: list[tuple] = (
            []
        )  # fallback: (headcount_gap, num_squads, score_gap, subset)

        for k in range(0, n + 1):
            for combo in combinations(range(n), k):
                chosen = [source_squads[i] for i in combo]
                moved = sum(s["size"] for s in chosen)
                if cap_remaining is not None and moved > cap_remaining:
                    continue
                new_source = source_total - moved
                new_dest = dest_total + moved
                if new_dest > MAX_TEAM_PLAYERS:
                    continue
                headcount_gap = abs(new_source - new_dest)
                moved_score = sum(s["score"] for s in chosen)
                score_gap = abs(
                    (source_score - moved_score) - (dest_score + moved_score)
                )
                if headcount_gap <= delta:
                    feasible.append((k, score_gap, chosen))
                elif headcount_gap < diff_before:
                    improving.append((headcount_gap, k, score_gap, chosen))

        if feasible:
            # Lowest achievable score gap, accepting the configured threshold.
            min_gap = min(item[1] for item in feasible)
            acceptable_gap = max(threshold, min_gap)
            candidates = [item for item in feasible if item[1] <= acceptable_gap + 1e-9]
            # Fewest squads, then lowest score gap.
            candidates.sort(key=lambda item: (item[0], item[1]))
            return candidates[0][2]

        if improving:
            # Cannot satisfy the headcount delta exactly; get as close as possible.
            improving.sort(key=lambda item: (item[0], item[1], item[2]))
            return improving[0][3]

        return []

    # ------------------------------------------------------------------ #
    # Pass 3 - average level balance (headcount-preserving swaps)
    # ------------------------------------------------------------------ #
    def _select_level_swaps(
        self,
        squads: dict,
        count_allies: int,
        count_axis: int,
        prior_moves: list[dict],
        cap_remaining: Optional[int],
    ) -> list[dict]:
        """Swap squads between teams to reduce the average player-level gap while
        keeping headcount within `max_players_per_team_delta`.

        A whole-squad move in one direction would unbalance the headcount when the
        teams are the same size, so level balancing is done as SWAPS: a squad from the
        higher average-level team is exchanged with a squad from the lower one. Only
        movable infantry squads not already moved by the earlier passes are considered
        (armor is balanced by its own pass).
        """
        delta = self.config.max_players_per_team_delta
        threshold = self.config.level_gap_threshold

        # Team headcount and level pools after the earlier passes.
        totals = {"allies": count_allies, "axis": count_axis}
        level_sum = {
            t: sum(s["level_sum"] for s in squads[t]) for t in ("allies", "axis")
        }
        level_count = {t: sum(s["size"] for s in squads[t]) for t in ("allies", "axis")}
        for move in prior_moves:
            src = move["team"]
            dst = "axis" if src == "allies" else "allies"
            totals[src] -= move["size"]
            totals[dst] += move["size"]
            level_sum[src] -= move["level_sum"]
            level_sum[dst] += move["level_sum"]
            level_count[src] -= move["size"]
            level_count[dst] += move["size"]

        moved_ids = {pid for m in prior_moves for pid in m["player_ids"]}
        pool = {
            t: [
                s
                for s in squads[t]
                if self._is_movable_infantry(s)
                and not any(pid in moved_ids for pid in s["player_ids"])
            ]
            for t in ("allies", "axis")
        }

        def avg(team: str) -> float:
            return level_sum[team] / level_count[team] if level_count[team] else 0.0

        swaps: list[dict] = []
        remaining = cap_remaining

        # Greedy: repeatedly apply the swap that most reduces the average-level gap.
        for _ in range(len(pool["allies"]) + len(pool["axis"]) + 1):
            gap = abs(avg("allies") - avg("axis"))
            if gap <= threshold:
                break
            high = "allies" if avg("allies") >= avg("axis") else "axis"
            low = "axis" if high == "allies" else "allies"

            best = None  # (new_gap, sq_high, sq_low)
            for sq_h in pool[high]:
                for sq_l in pool[low]:
                    pair_size = sq_h["size"] + sq_l["size"]
                    if remaining is not None and pair_size > remaining:
                        continue
                    new_high_total = totals[high] - sq_h["size"] + sq_l["size"]
                    new_low_total = totals[low] - sq_l["size"] + sq_h["size"]
                    if abs(new_high_total - new_low_total) > delta:
                        continue
                    high_ls = level_sum[high] - sq_h["level_sum"] + sq_l["level_sum"]
                    low_ls = level_sum[low] - sq_l["level_sum"] + sq_h["level_sum"]
                    high_lc = level_count[high] - sq_h["size"] + sq_l["size"]
                    low_lc = level_count[low] - sq_l["size"] + sq_h["size"]
                    if (
                        new_high_total > MAX_TEAM_PLAYERS
                        or new_low_total > MAX_TEAM_PLAYERS
                    ):
                        continue
                    high_avg = high_ls / high_lc if high_lc else 0.0
                    low_avg = low_ls / low_lc if low_lc else 0.0
                    new_gap = abs(high_avg - low_avg)
                    if new_gap < gap - 1e-9 and (best is None or new_gap < best[0]):
                        best = (new_gap, sq_h, sq_l)

            if best is None:
                break

            _, sq_h, sq_l = best
            totals[high] = totals[high] - sq_h["size"] + sq_l["size"]
            totals[low] = totals[low] - sq_l["size"] + sq_h["size"]
            level_sum[high] += sq_l["level_sum"] - sq_h["level_sum"]
            level_sum[low] += sq_h["level_sum"] - sq_l["level_sum"]
            level_count[high] += sq_l["size"] - sq_h["size"]
            level_count[low] += sq_h["size"] - sq_l["size"]
            pool[high].remove(sq_h)
            pool[low].remove(sq_l)
            swaps.append(sq_h)
            swaps.append(sq_l)
            if remaining is not None:
                remaining -= sq_h["size"] + sq_l["size"]
                if remaining <= 0:
                    break

        return swaps

    # ------------------------------------------------------------------ #
    # Execution
    # ------------------------------------------------------------------ #
    def _execute(self, rcon, moves: list[dict]) -> None:
        dry_run = self.config.dry_run
        author = AUTOMOD_USERNAME + ("-DryRun" if dry_run else "")

        if dry_run:
            self._switch_players(rcon, moves, author, dry_run=True)
            return

        self._notify_players(rcon, moves, author)
        delay = self.config.switch_delay_seconds
        if delay:
            self.logger.info(
                "Team balance: notified selected players; switching in %s seconds", delay
            )
            timer = Timer(delay, self._switch_players, args=(rcon, moves, author))
            timer.daemon = True
            timer.start()
            return

        self._switch_players(rcon, moves, author)

    def _notify_players(self, rcon, moves: list[dict], author: str) -> None:
        if not self.config.switch_message:
            return

        for squad in moves:
            for player_id, player_name in zip(
                squad["player_ids"], squad["player_names"]
            ):
                try:
                    rcon.message_player(
                        player_id=player_id,
                        message=self.config.switch_message,
                        by=author,
                        save_message=False,
                    )
                except Exception:
                    self.logger.warning(
                        "Team balance: could not message %s", player_name
                    )

    def _switch_players(
        self, rcon, moves: list[dict], author: str, dry_run: bool = False
    ) -> None:
        switched: list[str] = []

        for squad in moves:
            src = squad["team"]
            dst = "axis" if src == "allies" else "allies"

            # The target team can fill between move selection and execution. Recheck
            # each whole squad so this automod never knowingly pushes a team past 50.
            if not dry_run:
                try:
                    target_count = get_team_count(rcon.get_team_view(), dst)
                except Exception:
                    self.logger.exception(
                        "Team balance: could not recheck %s team capacity", dst
                    )
                    continue
                if target_count + squad["size"] > MAX_TEAM_PLAYERS:
                    self.logger.info(
                        "Team balance: skipping %s squad %s; %s would exceed %s players",
                        squad["type"],
                        squad["name"],
                        dst,
                        MAX_TEAM_PLAYERS,
                    )
                    continue

            for player_id, player_name in zip(
                squad["player_ids"], squad["player_names"]
            ):
                ok = True
                if not dry_run:
                    try:
                        ok = rcon.switch_player_now(player_id)
                    except Exception:
                        self.logger.warning(
                            "Team balance: failed to switch %s (%s)",
                            player_name,
                            player_id,
                        )
                        ok = False
                if not ok:
                    continue
                switched.append(
                    f"{player_name} [{squad['type']} {squad['name']}] {src} -> {dst}"
                )

        if not switched:
            return

        summary = (
            f"Team balance: moved {len(moves)} squad(s) / {len(switched)} player(s)"
            + (" (dry run)" if dry_run else "")
            + ":\n"
            + "\n".join(switched)
        )
        self.logger.info(summary)
        if self.config.discord_webhook_url is not None:
            try:
                send_to_discord_audit(
                    message=summary,
                    command_name="team_balance",
                    by=author,
                    webhookurls=[self.config.discord_webhook_url],
                )
            except Exception:
                self.logger.exception("Team balance: discord audit failed")
