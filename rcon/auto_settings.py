import logging
import os
import re
import time
from datetime import datetime

import pytz

from rcon.api_commands import get_rcon_api
from rcon.audit import ingame_mods, online_mods
from rcon.user_config.auto_settings import AutoSettingsConfig
from rcon.user_config.utils import BaseUserConfig

logger = logging.getLogger(__name__)

USER_CONFIG_NAME_PATTERN = re.compile(r"set_.*_config")

METRICS = {
    "player_count": lambda rcon: int(rcon.get_slots()["current_players"]),
    "online_mods": lambda: len(online_mods()),
    "ingame_mods": lambda: len(ingame_mods()),
    "current_map": lambda rcon: str(rcon.current_map),
    "time_of_day": lambda tz: datetime.now(tz=tz),
}
CONFIG_DIR = os.getenv("CONFIG_DIR", "config/")


def is_user_config_func(name: str) -> bool:
    return re.match(USER_CONFIG_NAME_PATTERN, name) is not None


class BaseCondition:
    def __init__(self, min=0, max=100, inverse=False, *args, **kwargs):
        self.min = int(min)
        self.max = int(max)
        self.inverse = bool(inverse)

        self.metric_name = ""
        self.metric_source = "rcon"

    @property
    def metric_getter(self):
        try:
            return METRICS[self.metric_name]
        except:
            return None

    def is_valid(self, **metric_sources):
        metric_source = metric_sources[self.metric_source]
        comparand = self.metric_getter(metric_source)
        res = self.min <= comparand <= self.max
        logger.info(
            "Applying condition %s: %s <= %s <= %s = %s. Inverse: %s",
            self.metric_name,
            self.min,
            comparand,
            self.max,
            res,
            self.inverse,
        )
        if self.inverse:
            return not res
        else:
            return res


class PlayerCountCondition(BaseCondition):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metric_name = "player_count"


class OnlineModsCondition(BaseCondition):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metric_name = "online_mods"
        self.metric_source = None

    def is_valid(self, **metric_sources):
        comparand = self.metric_getter()
        res = self.min <= comparand <= self.max
        logger.info(
            "Applying condition %s: %s <= %s <= %s = %s. Inverse: %s",
            self.metric_name,
            self.min,
            comparand,
            self.max,
            res,
            self.inverse,
        )
        if self.inverse:
            return not res
        else:
            return res


class IngameModsCondition(OnlineModsCondition):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metric_name = "ingame_mods"
        self.metric_source = None


class CurrentMapCondition(BaseCondition):
    def __init__(
        self, map_names=[], inverse=False, *args, **kwargs
    ):  # Avoid unexpected arguments
        self.map_names = map_names
        self.inverse = inverse
        self.metric_name = "current_map"
        self.metric_source = "rcon"

    def is_valid(self, **metric_sources):
        metric_source = metric_sources[self.metric_source]
        comparand = self.metric_getter(metric_source)
        res = comparand in self.map_names
        logger.info(
            "Applying condition %s: %s in %s = %s. Inverse: %s",
            self.metric_name,
            comparand,
            self.map_names,
            res,
            self.inverse,
        )
        if self.inverse:
            return not res
        else:
            return res


class TimeOfDayCondition(BaseCondition):
    def __init__(
        self, min="00:00", max="23:59", timezone="utc", inverse=False, *args, **kwargs
    ):  # Avoid unexpected arguments
        self.min = str(min)
        self.max = str(max)
        if self.max in ["24:00", "0:00"]:
            self.max = "23:59"
        self.inverse = bool(inverse)
        if timezone.lower() == "utc":
            self.tz = pytz.UTC
        else:
            self.tz = pytz.timezone(timezone)
        self.metric_name = "time_of_day"
        self.metric_source = None

    def is_valid(self, **metric_sources):
        try:
            min_h, min_m = [int(i) for i in self.min.split(":")[:2]]
            max_h, max_m = [int(i) for i in self.max.split(":")[:2]]
            min = datetime.now(tz=self.tz).replace(hour=min_h, minute=min_m)
            max = datetime.now(tz=self.tz).replace(hour=max_h, minute=max_m)
        except:
            logger.exception("Time Of Day condition is invalid and is ignored")
            return False  # The condition should fail
        comparand = datetime.now(tz=self.tz)
        res = min <= comparand <= max
        logger.info(
            "Applying condition %s: %s <= %s:%s <= %s = %s. Inverse: %s",
            self.metric_name,
            self.min,
            comparand.hour,
            comparand.minute,
            self.max,
            res,
            self.inverse,
        )
        if self.inverse:
            return not res
        else:
            return res


def create_condition(name, **kwargs):
    kwargs["inverse"] = kwargs.get("not", False)  # Using "not" would cause issues later
    if name == "player_count":
        return PlayerCountCondition(**kwargs)
    elif name == "online_mods":
        return OnlineModsCondition(**kwargs)
    elif name == "ingame_mods":
        return IngameModsCondition(**kwargs)
    elif name == "current_map":
        return CurrentMapCondition(**kwargs)
    elif name == "time_of_day":
        return TimeOfDayCondition(**kwargs)
    else:
        raise ValueError("Invalid condition type: %s" % name)


def do_run_commands(rcon, commands):
    for command, params in commands.items():
        try:
            logger.info("Applying %s %s", command, params)

            # Allow people to apply partial changes to a user config to make
            # auto settings less gigantic
            if is_user_config_func(command):
                # super dirty we should probably make an actual look up table
                # but all the names are consistent
                get_config_command = f"g{command[1:]}"
                config: BaseUserConfig = rcon.__getattribute__(get_config_command)()
                # get the existing config, override anything set in params
                merged_params = config.model_dump() | params
                rcon.__getattribute__(command)(**merged_params)
            else:
                # Non user config settings
                rcon.__getattribute__(command)(**params)
        except Exception as e:
            logger.exception("Unable to apply %s %s: %s", command, params, e)
        time.sleep(5)  # go easy on the server


def run():
    rcon = get_rcon_api()
    config = AutoSettingsConfig().get_settings()

    while True:
        always_apply_defaults = config.get("always_apply_defaults", False)
        can_invoke_multiple_rules = config.get("can_invoke_multiple_rules", False)
        default_commands = config.get("defaults", {})
        rule_matched = False
        if always_apply_defaults:
            # First run defaults so they can be overwritten. Save "set" commands so
            # we prevent them from being sent more than once in the same iteration.
            saved_commands = {
                name: params
                for (name, params) in default_commands.items()
                if name.startswith("set_")
            }
            do_run_commands(
                rcon,
                {
                    name: params
                    for (name, params) in default_commands.items()
                    if not name.startswith("set_")
                },
            )

        for rule in config["rules"]:
            conditions: list[BaseCondition] = []
            commands = rule.get("commands", {})
            for c_name, c_params in rule.get("conditions", {}).items():
                try:
                    conditions.append(create_condition(c_name, **c_params))
                except ValueError:
                    logger.exception(
                        "Invalid condition %s %s, ignoring...", c_name, c_params
                    )
                except pytz.UnknownTimeZoneError:
                    logger.exception(
                        "Invalid timezone for condition %s %s, ignoring...",
                        c_name,
                        c_params,
                    )

            if all([c.is_valid(rcon=rcon) for c in conditions]):
                if always_apply_defaults:
                    # Overwrites the saved commands in case they're duplicate
                    do_run_commands(rcon, {**saved_commands, **commands})
                else:
                    do_run_commands(rcon, commands)
                rule_matched = True
                if can_invoke_multiple_rules:
                    logger.info(
                        f"Rule conditions met, can invoke multiple rules and moving to next one. ({can_invoke_multiple_rules=})"
                    )
                    continue
                else:
                    logger.info(
                        f"Rule conditions met, cannot invoke multiple rules, ignoring potential other rules. ({can_invoke_multiple_rules=})"
                    )
                    break

            logger.info("Rule `%s` conditions not met, moving to next one.", rule)

        if not rule_matched:
            if always_apply_defaults:
                # The saved commands were never ran yet, so we do that here
                do_run_commands(rcon, saved_commands)
            else:
                do_run_commands(rcon, default_commands)
        time.sleep(60)


if __name__ == "__main__":
    try:
        run()
    except:
        logger.exception("Unable to run")
        exit(1)
