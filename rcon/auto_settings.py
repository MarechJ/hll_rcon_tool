import logging
import time

import pytz

from rcon.api_commands import get_rcon_api
from rcon.conditions import create_condition, Condition
from rcon.rcon import do_run_commands
from rcon.user_config.auto_settings import AutoSettingsConfig

logger = logging.getLogger(__name__)


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
            conditions: list[Condition] = []
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
