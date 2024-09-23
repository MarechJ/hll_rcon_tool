"""
Enforces the min/max global and per-role levels requirements
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
    NoLevelViolation,
    PunishDetails,
    PunishPlayer,
    PunishStepState,
    PunitionsToApply,
    WatchStatus,
)
from rcon.automods.num_or_inf import num_or_inf
from rcon.types import GameState, GetDetailedPlayer
from rcon.user_config.auto_mod_level import AutoModLevelUserConfig, Roles

LEVEL_THRESHOLDS_RESET_SECS = 120
AUTOMOD_USERNAME = "LevelThresholdsAutomod"


class LevelThresholdsAutomod:
    """
    Imported from rcon/automods/automod.py
    """

    logger: logging.Logger
    red: redis.StrictRedis
    config: AutoModLevelUserConfig

    def __init__(self, config: AutoModLevelUserConfig, red: redis.StrictRedis or None):
        self.logger = logging.getLogger(__name__)
        self.red = red
        self.config = config

    def enabled(self):
        """
        Global on/off switch
        """
        return self.config.enabled

    def on_connected(
        self, name: str, player_id: str, detailed_player_info: GetDetailedPlayer | None
    ) -> PunitionsToApply:
        """
        Sends a one-time levels rules reminder message to players on connect
        """
        p: PunitionsToApply = PunitionsToApply()

        min_level = self.config.min_level
        max_level = self.config.max_level

        if self.config.announcement_enabled and (
            min_level > 0 or max_level > 0 or self.config.level_thresholds
        ):
            # Initialize messages to empty string
            data = {
                "min_level_msg": "",
                "max_level_msg": "",
                "level_thresholds_msg": "",
            }

            # Populate min_level message if configured
            if min_level > 0:
                # only set info message if player level is impacted by the threshold
                if (
                    not self.config.only_announce_impacted_players
                    or detailed_player_info is None
                    or detailed_player_info["level"] < min_level
                ):
                    message = self.config.min_level_message
                    try:
                        message = message.format(level=min_level) + "\n"
                    except KeyError:
                        self.logger.warning(
                            "The automod message (%s) contains an invalid key", message
                        )
                    data["min_level_msg"] = message

            # Populate max_level message if configured
            if max_level > 0:
                # only set info message if player level is impacted by the threshold
                if (
                    not self.config.only_announce_impacted_players
                    or detailed_player_info is None
                    or detailed_player_info["level"] > max_level
                ):
                    message = self.config.max_level_message
                    try:
                        message = message.format(level=max_level) + "\n"
                    except KeyError:
                        self.logger.warning(
                            "The automod message (%s) contains an invalid key", message
                        )
                    data["max_level_msg"] = message

            # Populate level thresholds by role message if configured
            if self.config.level_thresholds:
                level_thresholds_msg = ""
                for role, role_config in self.config.level_thresholds.items():
                    # only set info message if player level is impacted by the threshold
                    if (
                        not self.config.only_announce_impacted_players
                        or detailed_player_info is None
                        or detailed_player_info["level"] < role_config.min_level
                    ):
                        message = self.config.violation_message
                        try:
                            message = (
                                message.format(
                                    role=role_config.label, level=role_config.min_level
                                )
                                + "\n"
                            )
                        except KeyError:
                            self.logger.warning(
                                "The automod message (%s) contains an invalid key",
                                message,
                            )
                        level_thresholds_msg += message
                data["level_thresholds_msg"] = level_thresholds_msg

            self.logger.debug("ON_CONNECTED: generated messages %s", data)

            # Format and send announcement message with previous data if required
            if (
                data.get("min_level_msg") != ""
                or data.get("max_level_msg") != ""
                or data.get("level_thresholds_msg") != ""
            ):
                message = self.config.announcement_message
                try:
                    message = message.format(**data)
                except KeyError:
                    self.logger.warning(
                        "The automod message (%s) contains an invalid key", message
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

    @contextmanager
    def watch_state(self, team: str, squad_name: str):
        """
        Observe and actualize the current moderation step
        """
        redis_key = f"level_thresholds_automod{team.lower()}{str(squad_name).lower()}"
        watch_status = self.red.get(redis_key)
        if watch_status:
            watch_status = pickle.loads(watch_status)
        # No punishments so far, starting a fresh one
        else:
            watch_status = WatchStatus()

        try:
            yield watch_status
        except NoLevelViolation:
            self.logger.debug(
                "Squad %s - %s no level violation, clearing state", team, squad_name
            )
            self.red.delete(redis_key)
        else:
            self.red.setex(
                redis_key, LEVEL_THRESHOLDS_RESET_SECS, pickle.dumps(watch_status)
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
            ActionMethod.FORCE_KICK: self.config.force_kick_message,
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

                # Global exclusion to avoid "Level 1" HLL bug
                if self.config.levelbug_enabled and aplayer.lvl == 1:
                    continue

                violations = []

                should_force_kick = False

                # Server min level threshold check
                min_level = self.config.min_level
                if (
                    min_level > 0
                    and aplayer.lvl < min_level
                    and not any(
                        flag_entry.flag in self.config.whitelist_flags
                        for flag_entry in aplayer.flags
                    )
                ):
                    message = self.config.min_level_message
                    try:
                        message = message.format(level=min_level)
                    except KeyError:
                        self.logger.warning(
                            "The automod message (%s) " "contains an invalid key",
                            message,
                        )
                    violations.append(message)
                    should_force_kick = True

                # Server max level threshold check
                max_level = self.config.max_level
                if (
                    aplayer.lvl > max_level > 0
                    and not any(
                        flag_entry.flag in self.config.whitelist_flags
                        for flag_entry in aplayer.flags
                    )
                ):
                    message = self.config.max_level_message
                    try:
                        message = message.format(level=max_level)
                    except KeyError:
                        self.logger.warning(
                            "The automod message (%s) " "contains an invalid key",
                            message,
                        )
                    violations.append(message)
                    should_force_kick = True

                # Force kick player if not matching global level thresholds
                if should_force_kick:
                    violation_msg = ", ".join(violations)
                    aplayer.details.message = self.get_message(
                        watch_status,
                        aplayer,
                        violation_msg,
                        ActionMethod.FORCE_KICK,
                    )
                    punitions_to_apply.kick.append(aplayer)
                    punitions_to_apply.add_squad_state(team, squad_name, squad)
                    continue

                # By role level thresholds check
                if self.config.level_thresholds:
                    role_config = self.config.level_thresholds.get(Roles(aplayer.role))

                    if (
                        role_config
                        and server_player_count >= role_config.min_players
                        and aplayer.lvl < role_config.min_level
                    ):
                        message = self.config.violation_message
                        try:
                            message = message.format(
                                role=role_config.label,
                                level=role_config.min_level,
                            )
                        except KeyError:
                            self.logger.warning(
                                "The automod message (%s) " "contains an invalid key",
                                message,
                            )
                        violations.append(message)

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

        # (not applicable)
        # immune_roles
        # immune_player_level

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

        # (not applicable)
        # immune_roles
        # immune_player_level

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

        # (not applicable)
        # immune_roles
        # immune_player_level

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
