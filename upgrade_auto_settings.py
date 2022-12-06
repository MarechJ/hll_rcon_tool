#!/usr/bin/env python

import json

# Setup logger
import logging
import os
import sys

from rcon.auto_settings import CONFIG_DIR
from rcon.user_config import AutoSettingsConfig

logging.basicConfig(format="[%(levelname)s] %(message)s", level=logging.INFO)
logging.info("Upgrading auto settings...")

"""

To upgrade, run the below command for each server instance.
Replace the container number with your server number.

docker-compose exec backend_1 /code/upgrade_auto_settings.py

"""


def get_config(filename):
    try:
        with open("%s%s" % (CONFIG_DIR, filename)) as f:
            return json.load(f)
    except FileNotFoundError:
        logging.info("Couldn't find config `config/%s`", filename)
        return None
    except json.JSONDecodeError:
        logging.info("Invlid JSON in config `config/%s`", filename)
        return None


def find_config(server_number):
    config = get_config(f"auto_settings_{server_number}.json")
    if not config:
        logging.info("No config for server number, falling back to common one")
        config = get_config("auto_settings.json")
    if not config:
        logging.warning(
            "Config 'auto_settings.json' not found. Falling back to default"
        )
        config = get_config("auto_settings.default.json")
    if not config:
        logging.error("Couldn't use default config 'auto_settings.default.json'")
    return config


SERVER_NUMBER = os.getenv("SERVER_NUMBER", 0)
if not SERVER_NUMBER:
    logging.fatal("Couldn't find Server Number in environment")
    sys.exit()


config = find_config(SERVER_NUMBER)
if not config:
    logging.fatal("No auto settings config file associated with this server")
    sys.exit()


try:
    new = dict(
        always_apply_defaults=False,
        defaults={
            command: params for (command, params) in config["player_count"]["defaults"]
        },
        rules=[],
    )

    for i, (condition, params, commands) in enumerate(config["player_count"]["rules"]):
        new_rule = dict(
            conditions={},
            commands={
                command: params
                for (command, params) in config["player_count"]["defaults"]
            },
        )

        if condition == "between":
            min, max = params
            new_rule["conditions"]["player_count"] = dict(min=min, max=max)
        elif condition == "equals":
            val = params[0]
            new_rule["conditions"]["player_count"] = dict(min=val, max=val)
        else:
            logging.warning("Invalid condition for rules[%s], skipping condition...", i)

        new["rules"].append(new_rule)

    AutoSettingsConfig().set_settings(new)

except Exception as e:
    logging.error("Failed to upgrade auto settings: %s: %s", e.__class__.__name__, e)
else:
    logging.info("Successfully upgraded auto settings")
