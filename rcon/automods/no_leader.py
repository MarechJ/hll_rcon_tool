import logging
import pickle
from contextlib import contextmanager
from datetime import datetime, timedelta

import redis

from rcon.automods.get_team_count import get_team_count
from rcon.automods.is_time import is_time
from rcon.automods.models import (
    ActionMethod,
    NoLeaderConfig,
    PunishDetails,
    PunishPlayer,
    PunishStepState,
    PunitionsToApply,
    SquadCycleOver,
    SquadHasLeader,
    WatchStatus,
)
from rcon.automods.num_or_inf import num_or_inf

LEADER_WATCH_RESET_SECS = 120
AUTOMOD_USERNAME = "NoLeaderWatch"


class NoLeaderAutomod:
    logger: logging.Logger
    red: redis.StrictRedis
    config: NoLeaderConfig

    def __init__(self, config: NoLeaderConfig, red: redis.StrictRedis or None):
        self.logger = logging.getLogger(__name__)
        self.red = red
        self.config = config

    def enabled(self):
        return self.config.enabled

    def get_message(
        self, watch_status: WatchStatus, aplayer: PunishPlayer, method: ActionMethod
    ):
        data = {}

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

    def player_punish_failed(self, aplayer):
        with self.watch_state(aplayer.team, aplayer.squad) as watch_status:
            try:
                if punishes := watch_status.punished.get(aplayer.name):
                    del punishes[-1]
            except Exception:
                self.logger.exception("tried to cleanup punished time but failed")

    @contextmanager
    def watch_state(self, team: str, squad_name: str):
        redis_key = f"no_leader_watch{team.lower()}{str(squad_name).lower()}"
        watch_status = self.red.get(redis_key)
        if watch_status:
            watch_status = pickle.loads(watch_status)
        else:  # No punishments so far, starting a fresh one
            watch_status = WatchStatus()

        try:
            yield watch_status
        except (SquadHasLeader, SquadCycleOver):
            self.logger.debug(
                "Squad %s - %s has a leader, clearing state", team, squad_name
            )
            self.red.delete(redis_key)
        else:
            self.red.setex(
                redis_key, LEADER_WATCH_RESET_SECS, pickle.dumps(watch_status)
            )

    def punitions_to_apply(
        self, team_view, squad_name: str, team: str, squad: dict
    ) -> PunitionsToApply:
        punitions_to_apply = PunitionsToApply()
        if not squad_name:
            self.logger.info("Skipping None or empty squad %s %s", squad_name, squad)
            return punitions_to_apply

        with self.watch_state(team, squad_name) as watch_status:
            if squad["has_leader"]:  # The squad has a leader, clearing punishments plan
                raise SquadHasLeader()

            if squad_name is None or squad is None:
                raise SquadHasLeader()

            self.logger.info("Squad %s - %s doesn't have leader", team, squad_name)
            author = AUTOMOD_USERNAME + ("-DryRun" if self.config.dry_run else "")

            for player in squad["players"]:
                aplayer = PunishPlayer(
                    steam_id_64=player["steam_id_64"],
                    name=player["name"],
                    team=team,
                    squad=squad_name,
                    role=player.get("role"),
                    lvl=int(player.get("level")),
                    details=PunishDetails(
                        author=author,
                        dry_run=self.config.dry_run,
                        discord_audit_url=self.config.discord_webhook_url,
                    ),
                )

                state = self.should_note_player(watch_status, squad_name, aplayer)
                if state == PunishStepState.APPLY:
                    punitions_to_apply.add_squad_state(team, squad_name, squad)
                if not state in [
                    PunishStepState.DISABLED,
                    PunishStepState.GO_TO_NEXT_STEP,
                ]:
                    continue

                state = self.should_warn_player(watch_status, squad_name, aplayer)

                if state == PunishStepState.APPLY:
                    aplayer.details.message = self.get_message(
                        watch_status, aplayer, ActionMethod.MESSAGE
                    )
                    punitions_to_apply.warning.append(aplayer)
                    punitions_to_apply.add_squad_state(team, squad_name, squad)
                if (
                    state == PunishStepState.WAIT
                ):  # only here to make the tests pass, otherwise useless
                    punitions_to_apply.add_squad_state(team, squad_name, squad)
                if not state in [
                    PunishStepState.DISABLED,
                    PunishStepState.GO_TO_NEXT_STEP,
                ]:
                    continue

                state = self.should_punish_player(
                    watch_status, team_view, squad_name, squad, aplayer
                )

                if state == PunishStepState.APPLY:
                    aplayer.details.message = self.get_message(
                        watch_status, aplayer, ActionMethod.PUNISH
                    )
                    punitions_to_apply.punish.append(aplayer)
                    punitions_to_apply.add_squad_state(team, squad_name, squad)
                if not state in [
                    PunishStepState.DISABLED,
                    PunishStepState.GO_TO_NEXT_STEP,
                ]:
                    continue

                state = self.should_kick_player(
                    watch_status, team_view, squad_name, squad, aplayer
                )
                if state == PunishStepState.APPLY:
                    aplayer.details.message = self.get_message(
                        watch_status, aplayer, ActionMethod.KICK
                    )
                    punitions_to_apply.kick.append(aplayer)
                    punitions_to_apply.add_squad_state(team, squad_name, squad)

        return punitions_to_apply

    def should_note_player(
        self, watch_status: WatchStatus, squad_name: str, aplayer: PunishPlayer
    ):
        if self.config.number_of_notes == 0:
            self.logger.debug("Notes are disabled. number_of_notes is set to 0")
            return PunishStepState.DISABLED

        notes = watch_status.noted.setdefault(aplayer.name, [])

        if not is_time(notes, self.config.notes_interval_seconds):
            self.logger.debug(
                "Waiting to note: %s in %s", aplayer.short_repr(), squad_name
            )
            return PunishStepState.WAIT

        if len(notes) < self.config.number_of_notes:
            self.logger.info(
                "%s Will be noted (%s/%s)",
                aplayer.short_repr(),
                len(notes),
                num_or_inf(self.config.number_of_notes),
            )
            notes.append(datetime.now())
            return PunishStepState.APPLY

        self.logger.info(
            "%s Max notes reached (%s/%s). Moving on to warn.",
            aplayer.short_repr(),
            len(notes),
            self.config.number_of_notes,
        )
        return PunishStepState.GO_TO_NEXT_STEP

    def should_warn_player(
        self, watch_status: WatchStatus, squad_name: str, aplayer: PunishPlayer
    ):
        if self.config.number_of_warning == 0:
            self.logger.debug("Warnings are disabled. number_of_warning is set to 0")
            return PunishStepState.DISABLED

        if (
            aplayer.lvl <= self.config.immuned_level_up_to
            or aplayer.role in self.config.immuned_roles
        ):
            self.logger.info("%s is immune to warnings", aplayer.short_repr())
            return PunishStepState.IMMUNED

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
        team_view,
        squad_name: str,
        squad,
        aplayer: PunishPlayer,
    ):
        if self.config.number_of_punish == 0:
            self.logger.debug("Punish is disabled")
            return PunishStepState.DISABLED

        if (
            get_team_count(team_view, "allies") + get_team_count(team_view, "axis")
        ) < self.config.disable_punish_below_server_player_count:
            self.logger.debug("Server below min player count for punish")
            return PunishStepState.WAIT

        if len(squad["players"]) < self.config.min_squad_players_for_punish:
            self.logger.debug("Squad %s below min player count for punish", squad_name)
            return PunishStepState.WAIT

        if (
            aplayer.lvl <= self.config.immuned_level_up_to
            or aplayer.role in self.config.immuned_roles
        ):
            self.logger.info("%s is immune to punishment", aplayer.short_repr())
            return PunishStepState.IMMUNED

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
        team_view,
        squad_name: str,
        squad,
        aplayer: PunishPlayer,
    ):
        if not self.config.kick_after_max_punish:
            self.logger.debug("Kick is disabled")
            return PunishStepState.DISABLED

        if (
            get_team_count(team_view, "allies") + get_team_count(team_view, "axis")
        ) < self.config.disable_kick_below_server_player_count:
            self.logger.debug("Server below min player count for punish")
            return PunishStepState.WAIT

        if len(squad["players"]) < self.config.min_squad_players_for_kick:
            self.logger.debug("Squad %s below min player count for punish", squad_name)
            return PunishStepState.WAIT

        if (
            aplayer.lvl <= self.config.immuned_level_up_to
            or aplayer.role in self.config.immuned_roles
        ):
            self.logger.info("%s is immune to kick", aplayer.short_repr())
            return PunishStepState.IMMUNED

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
