"""
Enforces the various seeding rules :
- disallowed roles
- disallowed weapons
- don't enter protected ennemy zone
"""

import logging
import pickle
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Literal

import redis

from rcon.automods.get_team_count import get_team_count
from rcon.automods.is_time import is_time
from rcon.automods.models import (
    ActionMethod,
    NoSeedingViolation,
    PunishDetails,
    PunishPlayer,
    PunishStepState,
    PunitionsToApply,
    WatchStatus,
)
from rcon.automods.num_or_inf import num_or_inf
from rcon.cache_utils import get_redis_client
from rcon.game_logs import on_match_start
from rcon.maps import GameMode, parse_layer
from rcon.rcon import StructuredLogLineType
from rcon.types import GameState, GetDetailedPlayer, Roles
from rcon.user_config.auto_mod_seeding import AutoModSeedingUserConfig

SEEDING_RULES_RESET_SECS = 120
AUTOMOD_USERNAME = "SeedingRulesAutomod"
SEEDING_RULE_NAMES = ["disallowed_roles", "disallowed_weapons", "enforce_cap_fight"]


def disabled_rule_key(rule: str) -> str:
    """
    Global off switch for
    disallowed_roles, disallowed_weapons and enforce_cap_fight rules
    according to the min/max players parameters set for each
    """
    return f"seeding_rules_automod_disabled_for_round_{rule}"


@on_match_start
def on_map_change(_, _1):
    """
    Resets the global off switch on map change for
    disallowed_roles, disallowed_weapons and enforce_cap_fight rules
    according to the min/max players parameters set for each
    """
    keys = []
    for rule in SEEDING_RULE_NAMES:
        keys.append(disabled_rule_key(rule))
    if len(keys) == 0:
        return
    get_redis_client().delete(*keys)


class SeedingRulesAutomod:
    """
    Imported from rcon/automods/automod.py
    """

    logger: logging.Logger
    red: redis.StrictRedis
    config: AutoModSeedingUserConfig

    def __init__(
        self, config: AutoModSeedingUserConfig, red: redis.StrictRedis or None
    ):
        self.logger = logging.getLogger(__name__)
        self.red = red
        self.config = config

    def enabled(self) -> bool:
        """
        Global on/off switch
        """
        return self.config.enabled

    def on_connected(
        self,
        name: str,
        player_id: str,
        detailed_player_info: GetDetailedPlayer | None = None,
    ) -> PunitionsToApply:
        """
        Sends a one-time seeding rules reminder message to players on connect
        """
        p: PunitionsToApply = PunitionsToApply()

        disallowed_roles = set(self.config.disallowed_roles.roles.values())
        disallowed_weapons = set(self.config.disallowed_weapons.weapons.values())
        enforce_cap_fight_maxplayers = self.config.enforce_cap_fight.max_players

        if self.config.announcement_enabled and (
            len(disallowed_roles) != 0
            or len(disallowed_weapons) != 0
            or enforce_cap_fight_maxplayers != 0
        ):
            if all([self._is_seeding_rule_disabled(r) for r in SEEDING_RULE_NAMES]):
                return p

            data = {
                "disallowed_roles": ", ".join(disallowed_roles),
                "disallowed_roles_max_players": self.config.disallowed_roles.max_players,
                "disallowed_weapons": ", ".join(disallowed_weapons),
                "disallowed_weapons_max_players": self.config.disallowed_weapons.max_players,
            }
            message = self.config.announcement_message
            try:
                message = message.format(**data)
            except KeyError:
                self.logger.warning(
                    "The automod message contains an invalid key for disallowed_roles and/or disallowed_weapons (%s)",
                    message,
                )

            author = AUTOMOD_USERNAME + ("-DryRun" if self.config.dry_run else "")

            p.warning.append(
                PunishPlayer(
                    player_id=player_id,
                    name=name,
                    squad="",
                    team="",
                    flags=[],
                    role="",
                    lvl=0,
                    details=PunishDetails(
                        author=author,
                        dry_run=self.config.dry_run,
                        discord_audit_url=self.config.discord_webhook_url,
                        message=message,
                    ),
                )
            )

        return p

    def on_kill(self, log: StructuredLogLineType) -> PunitionsToApply:
        """
        Observe weapon usage
        Punishes the trespasser if a kill using a forbidden weapon has been logged
        """
        p: PunitionsToApply = PunitionsToApply()

        if log[
            "weapon"
        ] in self.config.disallowed_weapons.weapons and not self._is_seeding_rule_disabled(
            "disallowed_weapons"
        ):
            author = AUTOMOD_USERNAME + ("-DryRun" if self.config.dry_run else "")

            aplayer = PunishPlayer(
                player_id=log["player_id_1"],
                name=log["player_name_1"],
                squad="",
                team="",
                flags=[],
                role="",
                lvl=0,
                details=PunishDetails(
                    author=author,
                    dry_run=self.config.dry_run,
                    discord_audit_url=self.config.discord_webhook_url,
                ),
            )
            data = {
                "player_name": aplayer.name,
                "weapon": self.config.disallowed_weapons.weapons.get(log["weapon"]),
            }
            message = self.config.disallowed_weapons.violation_message
            try:
                message = message.format(**data)
            except KeyError:
                self.logger.warning(
                    "The automod message for disallowed weapons (%s) contains an invalid key",
                    message,
                )
            aplayer.details.message = message

            p.punish.append(aplayer)

        return p

    @contextmanager
    def watch_state(self, team: str, squad_name: str):
        """
        Observe and actualize the current moderation step
        """
        redis_key = f"seeding_rules_automod{team.lower()}{str(squad_name).lower()}"
        watch_status = self.red.get(redis_key)
        if watch_status:
            watch_status = pickle.loads(watch_status)
        else:  # No punishments so far, starting a fresh one
            watch_status = WatchStatus()

        try:
            yield watch_status
        except NoSeedingViolation:
            self.logger.debug(
                "Squad %s - %s no seeding violation, clearing state", team, squad_name
            )
            self.red.delete(redis_key)
        else:
            self.red.setex(
                redis_key, SEEDING_RULES_RESET_SECS, pickle.dumps(watch_status)
            )

    def get_message(
        self,
        watch_status: WatchStatus,
        aplayer: PunishPlayer,
        violation_msg: str,
        method: ActionMethod,
    ):
        """
        Construct the message sent to the player
        according to the actual moderation step
        """
        data: dict[str, str | int] = {
            "violation": violation_msg,
        }

        if method == ActionMethod.MESSAGE:
            data["received_warnings"] = len(watch_status.warned.get(aplayer.name))
            data["max_warnings"] = self.config.number_of_warnings
            data["next_check_seconds"] = self.config.warning_interval_seconds

        if method == ActionMethod.PUNISH:
            data["received_punishes"] = len(watch_status.punished.get(aplayer.name))
            data["max_punishes"] = self.config.number_of_punishments
            data["next_check_seconds"] = self.config.punish_interval_seconds

        if method == ActionMethod.KICK:
            data["kick_grace_period"] = self.config.kick_grace_period_seconds

        data["player_name"] = aplayer.name
        data["squad_name"] = aplayer.squad

        base_message = {
            ActionMethod.MESSAGE: self.config.warning_message,
            ActionMethod.PUNISH: self.config.punish_message,
            ActionMethod.KICK: self.config.kick_message,
        }

        message = base_message[method]
        try:
            return message.format(**data)
        except KeyError:
            self.logger.warning(
                "The automod message of %s (%s) contains an invalid key",
                repr(method),
                message,
            )
            return message

    def _disable_for_round(self, rule: str):
        self.red.setex(disabled_rule_key(rule), 3 * 60 * 60, "1")

    def _enable_for_round(self, rule: str):
        self.red.delete(disabled_rule_key(rule))

    def _is_seeding_rule_disabled(self, rule: str) -> bool:
        k = disabled_rule_key(rule)
        if not self.red.exists(k):
            return False

        v = self.red.get(disabled_rule_key(rule))
        if isinstance(v, bytes):
            v = v.decode()
        return v == "1"

    def player_punish_failed(self, aplayer):
        """
        A dead/unspawned player can't be punished
        Resets the timer from the last unsuccessful punish.
        """
        with self.watch_state(aplayer.team, aplayer.squad) as watch_status:
            try:
                if punishes := watch_status.punished.get(aplayer.name):
                    del punishes[-1]
            except Exception:
                self.logger.exception("tried to cleanup punished time but failed")

    def punitions_to_apply(
        self,
        team_view,
        squad_name: str,
        team: Literal["axis", "allies"],
        squad: dict,
        game_state: GameState,
    ) -> PunitionsToApply:
        """
        Observe all squads/players
        Find the ones who trespass rules
        Sends them to their next moderation step
        """
        self.logger.debug("Squad %s %s", squad_name, squad)
        punitions_to_apply = PunitionsToApply()

        server_player_count = get_team_count(team_view, "allies") + get_team_count(
            team_view, "axis"
        )

        # dont_do_anything_below_this_number_of_players
        if (
            server_player_count
            < self.config.dont_do_anything_below_this_number_of_players
        ):
            self.logger.debug("Server below min player count : disabling")
            return punitions_to_apply

        if not squad_name:
            self.logger.debug(
                "Skipping None or empty squad - (%s) %s", team, squad_name
            )
            return punitions_to_apply

        with self.watch_state(team, squad_name) as watch_status:

            # if squad_name is None or squad is None:
            #     raise NoSeedingViolation()

            author = AUTOMOD_USERNAME + ("-DryRun" if self.config.dry_run else "")

            for player in squad["players"]:
                aplayer = PunishPlayer(
                    player_id=player["player_id"],
                    name=player["name"],
                    squad=squad_name,
                    team=team,
                    flags=player.get("profile", {}).get("flags", []),
                    role=player.get("role"),
                    lvl=int(player.get("level")),
                    details=PunishDetails(
                        author=author,
                        dry_run=self.config.dry_run,
                        discord_audit_url=self.config.discord_webhook_url,
                    ),
                )

                drc = self.config.disallowed_roles
                if (
                    server_player_count < drc.min_players
                    or server_player_count >= drc.max_players
                ):
                    self._disable_for_round("disallowed_roles")
                else:
                    self._enable_for_round("disallowed_roles")

                dwc = self.config.disallowed_weapons
                if (
                    server_player_count < dwc.min_players
                    or server_player_count >= dwc.max_players
                ):
                    self._disable_for_round("disallowed_weapons")
                else:
                    self._enable_for_round("disallowed_weapons")

                ecf = self.config.enforce_cap_fight
                if (
                    server_player_count < ecf.min_players
                    or server_player_count >= ecf.max_players
                ):
                    self._disable_for_round("enforce_cap_fight")
                else:
                    self._enable_for_round("enforce_cap_fight")

                violations = []

                if (
                    not self._is_seeding_rule_disabled("disallowed_roles")
                    and drc.min_players <= server_player_count < drc.max_players
                ):
                    if Roles(aplayer.role) in drc.roles:
                        violations.append(
                            drc.violation_message.format(
                                role=drc.roles.get(Roles(aplayer.role))
                            )
                        )

                layer = parse_layer(game_state["current_map"]["id"])
                if layer.game_mode != GameMode.WARFARE:
                    self._disable_for_round("enforce_cap_fight")

                if not self._is_seeding_rule_disabled("enforce_cap_fight") and (
                    (team == "axis" and game_state["axis_score"] >= ecf.max_caps)
                    or (team == "allies" and game_state["allied_score"] >= ecf.max_caps)
                ):
                    self.logger.debug("Player is on %s side and winning", team)
                    op = player["offense"]
                    oop = watch_status.offensive_points.setdefault(aplayer.name, -1)

                    self.logger.debug(
                        "Player had %s offensive points last and now %s",
                        str(oop),
                        str(op),
                    )
                    if oop != -1 and oop < op:
                        violations.append(ecf.violation_message)

                        if ecf.skip_warning:
                            warnings = watch_status.warned.setdefault(aplayer.name, [])
                            for _ in range(self.config.number_of_warnings):
                                warnings.append(
                                    datetime.now()
                                    - timedelta(
                                        seconds=self.config.warning_interval_seconds + 1
                                    )
                                )
                    watch_status.offensive_points[aplayer.name] = op
                else:
                    watch_status.offensive_points.clear()

                if len(violations) == 0:
                    continue

                violation_msg = ", ".join(violations)

                # Note (not applicable)

                # Warning
                state = self.should_warn_player(watch_status, squad_name, aplayer)

                if state == PunishStepState.APPLY:
                    aplayer.details.message = self.get_message(
                        watch_status, aplayer, violation_msg, ActionMethod.MESSAGE
                    )
                    punitions_to_apply.warning.append(aplayer)
                    punitions_to_apply.add_squad_state(team, squad_name, squad)

                if state == PunishStepState.WAIT:
                    # only here to make the tests pass, otherwise useless
                    punitions_to_apply.add_squad_state(team, squad_name, squad)

                if state not in [
                    PunishStepState.DISABLED,
                    PunishStepState.GO_TO_NEXT_STEP,
                ]:
                    continue

                # Punish
                state = self.should_punish_player(
                    watch_status, team_view, squad_name, squad, aplayer
                )

                if state == PunishStepState.APPLY:
                    aplayer.details.message = self.get_message(
                        watch_status, aplayer, violation_msg, ActionMethod.PUNISH
                    )
                    punitions_to_apply.punish.append(aplayer)
                    punitions_to_apply.add_squad_state(team, squad_name, squad)

                if state not in [
                    PunishStepState.DISABLED,
                    PunishStepState.GO_TO_NEXT_STEP,
                ]:
                    continue

                # Kick
                state = self.should_kick_player(
                    watch_status, team_view, squad_name, squad, aplayer
                )

                if state == PunishStepState.APPLY:
                    aplayer.details.message = self.get_message(
                        watch_status, aplayer, violation_msg, ActionMethod.KICK
                    )
                    punitions_to_apply.kick.append(aplayer)
                    punitions_to_apply.add_squad_state(team, squad_name, squad)

                if state not in [
                    PunishStepState.DISABLED,
                    PunishStepState.GO_TO_NEXT_STEP,
                ]:
                    continue

        return punitions_to_apply

    # (not applicable)
    # def should_note_player()

    def should_warn_player(
        self, watch_status: WatchStatus, squad_name: str, aplayer: PunishPlayer
    ):
        """
        Send a message to trespassers
        telling them they must follow the rules
        before being punished and kicked
        """
        # number_of_warnings
        if self.config.number_of_warnings == 0:
            self.logger.debug("Warnings are disabled. number_of_warning is set to 0")
            return PunishStepState.DISABLED

        # whitelist_flags
        if any(
            flag_entry.flag in self.config.whitelist_flags
            for flag_entry in aplayer.flags
        ):
            self.logger.debug("%s is immune to warnings", aplayer.short_repr())
            return PunishStepState.IMMUNED

        # immune_roles
        # immune_player_level
        if (
            aplayer.lvl <= self.config.immune_player_level
            or aplayer.role in self.config.immune_roles
        ):
            self.logger.debug("%s is immune to warnings", aplayer.short_repr())
            return PunishStepState.IMMUNED

        warnings = watch_status.warned.setdefault(aplayer.name, [])

        # warning_interval_seconds
        if not is_time(warnings, self.config.warning_interval_seconds):
            self.logger.debug(
                "Waiting to warn: %s in %s", aplayer.short_repr(), squad_name
            )
            return PunishStepState.WAIT

        # number_of_warnings
        if (
            len(warnings) < self.config.number_of_warnings
            or self.config.number_of_warnings == -1
        ):
            self.logger.info(
                "%s Will be warned (%s/%s)",
                aplayer.short_repr(),
                len(warnings),
                num_or_inf(self.config.number_of_warnings),
            )
            warnings.append(datetime.now())
            return PunishStepState.APPLY

        self.logger.info(
            "%s Max warnings reached (%s/%s). Moving on to punish.",
            aplayer.short_repr(),
            len(warnings),
            self.config.number_of_warnings,
        )
        return PunishStepState.GO_TO_NEXT_STEP

    def should_punish_player(
        self,
        watch_status: WatchStatus,
        team_view,
        squad_name: str,
        squad,
        aplayer: PunishPlayer,
    ):
        """
        Punish (kill) trespassers
        telling them they must follow the rules
        before being kicked
        """
        # number_of_punishments
        if self.config.number_of_punishments == 0:
            self.logger.debug("Punish is disabled")
            return PunishStepState.DISABLED

        # whitelist_flags
        if any(
            flag_entry.flag in self.config.whitelist_flags
            for flag_entry in aplayer.flags
        ):
            self.logger.debug("%s is immune to punishment", aplayer.short_repr())
            return PunishStepState.IMMUNED

        # immune_roles
        # immune_player_level
        if (
            aplayer.lvl <= self.config.immune_player_level
            or aplayer.role in self.config.immune_roles
        ):
            self.logger.debug("%s is immune to punishment", aplayer.short_repr())
            return PunishStepState.IMMUNED

        # min_squad_players_for_punish
        if len(squad["players"]) < self.config.min_squad_players_for_punish:
            self.logger.debug("Squad %s below min player count for punish", squad_name)
            return PunishStepState.WAIT

        # min_server_players_for_punish
        if (
            get_team_count(team_view, "allies") + get_team_count(team_view, "axis")
        ) < self.config.min_server_players_for_punish:
            self.logger.debug("Server below min player count for punish")
            return PunishStepState.WAIT

        punishes = watch_status.punished.setdefault(aplayer.name, [])

        # punish_interval_seconds
        if not is_time(punishes, self.config.punish_interval_seconds):
            self.logger.debug("Waiting to punish %s", squad_name)
            return PunishStepState.WAIT

        # number_of_punishments
        if (
            len(punishes) < self.config.number_of_punishments
            or self.config.number_of_punishments == -1
        ):
            self.logger.info(
                "%s Will be punished (%s/%s)",
                aplayer.short_repr(),
                len(punishes),
                num_or_inf(self.config.number_of_punishments),
            )
            punishes.append(datetime.now())
            return PunishStepState.APPLY

        self.logger.info(
            "%s Max punish reached (%s/%s)",
            aplayer.short_repr(),
            len(punishes),
            self.config.number_of_punishments,
        )
        return PunishStepState.GO_TO_NEXT_STEP

    def should_kick_player(
        self,
        watch_status: WatchStatus,
        team_view,
        squad_name: str,
        squad,
        aplayer: PunishPlayer,
    ):
        """
        Kick (disconnect) trespassers
        telling them they must follow the rules
        """
        # kick_after_max_punish
        if not self.config.kick_after_max_punish:
            self.logger.debug("Kick is disabled")
            return PunishStepState.DISABLED

        # whitelist_flags
        if any(
            flag_entry.flag in self.config.whitelist_flags
            for flag_entry in aplayer.flags
        ):
            self.logger.debug("%s is immune to kick", aplayer.short_repr())
            return PunishStepState.IMMUNED

        # immune_roles
        # immune_player_level
        if (
            aplayer.lvl <= self.config.immune_player_level
            or aplayer.role in self.config.immune_roles
        ):
            self.logger.debug("%s is immune to kick", aplayer.short_repr())
            return PunishStepState.IMMUNED

        # min_squad_players_for_kick
        if len(squad["players"]) < self.config.min_squad_players_for_kick:
            self.logger.debug("Squad %s below min player count for punish", squad_name)
            return PunishStepState.WAIT

        # min_server_players_for_kick
        if (
            get_team_count(team_view, "allies") + get_team_count(team_view, "axis")
        ) < self.config.min_server_players_for_kick:
            self.logger.debug("Server below min player count for punish")
            return PunishStepState.WAIT

        try:
            last_time = watch_status.punished.get(aplayer.name, [])[-1]
        except IndexError:
            self.logger.error("Trying to kick player without prior punishes")
            return PunishStepState.DISABLED

        # kick_grace_period_seconds
        if datetime.now() - last_time < timedelta(
            seconds=self.config.kick_grace_period_seconds
        ):
            return PunishStepState.WAIT

        return PunishStepState.APPLY
