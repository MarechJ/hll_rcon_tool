import logging
import pickle
from contextlib import contextmanager
from datetime import datetime, timedelta

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
    SeedingRulesConfig,
    WatchStatus,
)
from rcon.automods.num_or_inf import num_or_inf
from rcon.cache_utils import get_redis_client
from rcon.extended_commands import StructuredLogLine
from rcon.game_logs import on_match_start

SEEDING_RULES_RESET_SECS = 120
AUTOMOD_USERNAME = "SeedingRulesAutomod"
SEEDING_RULE_NAMES = ["disallowed_roles", "disallowed_weapons"]


def disabled_rule_key(rule: str) -> str:
    return f"seeding_rules_automod_disabled_for_round_{rule}"


@on_match_start
def on_map_change(_, _1):
    keys = []
    for rule in SEEDING_RULE_NAMES:
        keys.append(disabled_rule_key(rule))
    if len(keys) == 0:
        return
    get_redis_client().delete(*keys)


class SeedingRulesAutomod:
    logger: logging.Logger
    red: redis.StrictRedis
    config: SeedingRulesConfig

    def __init__(self, config: SeedingRulesConfig, red: redis.StrictRedis or None):
        self.logger = logging.getLogger(__name__)
        self.red = red
        self.config = config

    def enabled(self):
        return self.config.enabled

    @contextmanager
    def watch_state(self, team: str, squad_name: str):
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
                "Squad %s - %s no seeding violation clearing state", team, squad_name
            )
            self.red.delete(redis_key)
        else:
            self.red.setex(
                redis_key, SEEDING_RULES_RESET_SECS, pickle.dumps(watch_status)
            )

    def on_connected(self, name: str, steam_id_64: str) -> PunitionsToApply:
        p: PunitionsToApply = PunitionsToApply()

        disallowed_roles = set(self.config.disallowed_roles.roles.values())
        disallowed_weapons = set(self.config.disallowed_weapons.weapons.values())

        if self.config.announce_seeding_active.enabled and (
            len(disallowed_weapons) != 0 or len(disallowed_weapons) != 0
        ):
            if all(
                [self._is_seeding_rule_disabled(r) is True for r in SEEDING_RULE_NAMES]
            ):
                return p

            data = {
                "disallowed_roles": ", ".join(disallowed_roles),
                "disallowed_roles_max_players": self.config.disallowed_roles.max_players,
                "disallowed_weapons": ", ".join(disallowed_weapons),
                "disallowed_weapons_max_players": self.config.disallowed_weapons.max_players,
            }
            message = self.config.announce_seeding_active.message
            try:
                message = message.format(**data)
            except KeyError:
                self.logger.warning(
                    f"The automod message for disallowed weapons ({message}) contains an invalid key"
                )

            p.warning.append(
                PunishPlayer(
                    steam_id_64=steam_id_64,
                    name=name,
                    squad="",
                    team="",
                    role="",
                    lvl=0,
                    details=PunishDetails(
                        author=AUTOMOD_USERNAME,
                        dry_run=False,
                        discord_audit_url=self.config.discord_webhook_url,
                        message=message,
                    ),
                )
            )

        return p

    def on_kill(self, log: StructuredLogLine) -> PunitionsToApply:
        p: PunitionsToApply = PunitionsToApply()

        if log[
            "weapon"
        ] in self.config.disallowed_weapons.weapons and not self._is_seeding_rule_disabled(
            "disallowed_weapons"
        ):
            aplayer = PunishPlayer(
                steam_id_64=log["steam_id_64_1"],
                name=log["player"],
                squad="",
                team="",
                role="",
                lvl=0,
                details=PunishDetails(
                    author=AUTOMOD_USERNAME,
                    dry_run=False,
                    discord_audit_url=self.config.discord_webhook_url,
                ),
            )
            data = {
                "player_name": aplayer.name,
                "weapon": self.config.disallowed_weapons.weapons.get(log["weapon"]),
            }
            message = self.config.disallowed_weapons.message
            try:
                message = message.format(**data)
            except KeyError:
                self.logger.warning(
                    f"The automod message for disallowed weapons ({message}) contains an invalid key"
                )
            aplayer.details.message = message

            p.punish.append(aplayer)

        return p

    def get_message(
        self,
        watch_status: WatchStatus,
        aplayer: PunishPlayer,
        violation_msg: str,
        method: ActionMethod,
    ):
        data = {
            "violation": violation_msg,
        }

        if method == ActionMethod.MESSAGE:
            data["received_warnings"] = len(watch_status.warned.get(aplayer.name))
            data["max_warnings"] = self.config.number_of_warning
            data["next_check_seconds"] = self.config.warning_interval_seconds
        if method == ActionMethod.PUNISH:
            data["received_punishes"] = len(watch_status.punished.get(aplayer.name))
            data["max_punishes"] = self.config.number_of_punish
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
                f"The automod message of {repr(method)} ({message}) contains an invalid key"
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

    def punitions_to_apply(
        self, team_view, squad_name: str, team: str, squad: dict
    ) -> PunitionsToApply:
        punitions_to_apply = PunitionsToApply()
        if not squad_name:
            self.logger.info("Skipping None or empty squad %s %s", squad_name, squad)
            return punitions_to_apply

        server_player_count = get_team_count(team_view, "allies") + get_team_count(
            team_view, "axis"
        )

        with self.watch_state(team, squad_name) as watch_status:
            if squad_name is None or squad is None:
                raise NoSeedingViolation()

            for player in squad["players"]:
                aplayer = PunishPlayer(
                    steam_id_64=player["steam_id_64"],
                    name=player["name"],
                    team=team,
                    squad=squad_name,
                    role=player.get("role"),
                    lvl=int(player.get("level")),
                    details=PunishDetails(
                        author=AUTOMOD_USERNAME,
                        dry_run=False,
                        discord_audit_url=self.config.discord_webhook_url,
                    ),
                )

                drc = self.config.disallowed_roles
                if server_player_count >= drc.max_players:
                    self._disable_for_round("disallowed_roles")

                dwc = self.config.disallowed_weapons
                if dwc.max_players > server_player_count >= dwc.min_players:
                    self._enable_for_round("disallowed_weapons")
                if server_player_count >= dwc.max_players:
                    self._disable_for_round("disallowed_weapons")

                violations = []
                if (
                    not self._is_seeding_rule_disabled("disallowed_roles")
                    and drc.min_players <= server_player_count < drc.max_players
                ):
                    if aplayer.role in drc.roles:
                        violations.append(
                            drc.message.format(role=drc.roles.get(aplayer.role))
                        )

                if len(violations) == 0:
                    continue

                violation_msg = ", ".join(violations)
                state = self.should_warn_player(watch_status, squad_name, aplayer)

                if state == PunishStepState.APPLY:
                    aplayer.details.message = self.get_message(
                        watch_status, aplayer, violation_msg, ActionMethod.MESSAGE
                    )
                    punitions_to_apply.warning.append(aplayer)
                    punitions_to_apply.add_squad_state(team, squad_name, squad)

                if state not in [
                    PunishStepState.DISABLED,
                    PunishStepState.GO_TO_NEXT_STEP,
                ]:
                    continue

                state = self.should_punish_player(watch_status, squad_name, aplayer)

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

                state = self.should_kick_player(watch_status, aplayer)

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

    def should_warn_player(
        self, watch_status: WatchStatus, squad_name: str, aplayer: PunishPlayer
    ):
        if self.config.number_of_warning == 0:
            self.logger.debug("Warnings are disabled. number_of_warning is set to 0")
            return PunishStepState.DISABLED

        warnings = watch_status.warned.setdefault(aplayer.name, [])

        if not is_time(warnings, self.config.warning_interval_seconds):
            self.logger.debug(
                "Waiting to warn: %s in %s", aplayer.short_repr(), squad_name
            )
            return PunishStepState.WAIT

        if (
            len(warnings) < self.config.number_of_warning
            or self.config.number_of_warning == -1
        ):
            self.logger.info(
                "%s Will be warned (%s/%s)",
                aplayer.short_repr(),
                len(warnings),
                num_or_inf(self.config.number_of_warning),
            )
            warnings.append(datetime.now())
            return PunishStepState.APPLY

        self.logger.info(
            "%s Max warnings reached (%s/%s). Moving on to punish.",
            aplayer.short_repr(),
            len(warnings),
            self.config.number_of_warning,
        )
        return PunishStepState.GO_TO_NEXT_STEP

    def should_punish_player(
        self,
        watch_status: WatchStatus,
        squad_name: str,
        aplayer: PunishPlayer,
    ):
        if self.config.number_of_punish == 0:
            self.logger.debug("Punish is disabled")
            return PunishStepState.DISABLED

        punishes = watch_status.punished.setdefault(aplayer.name, [])

        if not is_time(punishes, self.config.punish_interval_seconds):
            self.logger.debug("Waiting to punish %s", squad_name)
            return PunishStepState.WAIT

        if (
            len(punishes) < self.config.number_of_punish
            or self.config.number_of_punish == -1
        ):
            self.logger.info(
                "%s Will be punished (%s/%s)",
                aplayer.short_repr(),
                len(punishes),
                num_or_inf(self.config.number_of_punish),
            )
            punishes.append(datetime.now())
            return PunishStepState.APPLY

        self.logger.info(
            "%s Max punish reached (%s/%s)",
            aplayer.short_repr(),
            len(punishes),
            self.config.number_of_punish,
        )
        return PunishStepState.GO_TO_NEXT_STEP

    def should_kick_player(
        self,
        watch_status: WatchStatus,
        aplayer: PunishPlayer,
    ):
        if not self.config.kick_after_max_punish:
            self.logger.debug("Kick is disabled")
            return PunishStepState.DISABLED

        try:
            last_time = watch_status.punished.get(aplayer.name, [])[-1]
        except IndexError:
            self.logger.error("Trying to kick player without prior punishes")
            return PunishStepState.DISABLED

        if datetime.now() - last_time < timedelta(
            seconds=self.config.kick_grace_period_seconds
        ):
            return PunishStepState.WAIT

        return PunishStepState.APPLY
