import logging
import time
import json
import os
from rcon.extended_commands import Rcon
from rcon.settings import SERVER_INFO

logger = logging.getLogger(__name__)


def compare(operand, operator, arguments):
    if operator == "between":
        start, end = arguments
        return start <= operand <= end
    if operator == "equals":
        return operand == arguments[0]
    return False


METRICS = {"player_count": lambda rcon: int(rcon.get_slots().split('/')[0])}
CONFIG_DIR = os.getenv('CONFIG_DIR', 'config/')

class MetricCondition:
    def __init__(self, name, metric_getter, config):
        self.metric_getter = metric_getter
        self.default_commands = config["defaults"]
        self.rules = config["rules"]
        self.name = name

    def run_commands(self, rcon, commands):
        for command, params in commands:
            # TODO it might be better to use the API however this process is not aware of it
            try:
                logger.info("Applying %s %s", command, params)
                rcon.__getattribute__(command)(**params)
            except:
                logger.exception("Unable to apply %s %s", command, params)
            time.sleep(10)  # go easy on the server

    def apply(self, rcon):
        # Todo impllement throttling in here and make it configurable
        for comparator, arguments, commands in self.rules:
            metric = self.metric_getter(rcon)
            if compare(metric, comparator, arguments):
                logger.info("Apply rule for %s %s %s", self.name, comparator, arguments)
                self.run_commands(rcon, commands)
                return  # Don't run other rules

        logger.info("Applying default rule for %s", self.name)
        return self.run_commands(rcon, self.default_commands)


def get_config(filename):
    try:
        with open("%s%s" % (CONFIG_DIR, filename)) as f:
            return json.load(f)
    except FileNotFoundError:
        logger.exception("Invlid JSON in config `config/%s`", filename)
        return None
    except json.JSONDecodeError:
        logger.exception("Couldn't find config `config/%s`", filename)
        return None


def run():
    rcon = Rcon(SERVER_INFO)
    server_number = os.getenv("SERVER_NUMBER")
    config = get_config(f"auto_settings_{server_number}.json")
    if not config:
        logger.warning("No config for server number, falling back to common one")
        config = get_config("auto_settings.json")
    if not config:
        logger.warning("Config 'auto_settings.json' not found. Falling back to default")
        config = get_config("auto_settings.default.json")
    if not config:
        logger.fatal("Couldn't use default config 'auto_settings.default.json' exiting")
        exit(1)

    try:
        conditions = [
            MetricCondition(name, METRICS[name], config)
            for name, config in config.items()
        ]
    except KeyError as e:
        logger.fatal("Invalid metric %s", e)
        exit(1)

    while True:
        for c in conditions:
            c.apply(rcon)
        time.sleep(60)


if __name__ == "__main__":
    try:
        run()
    except:
        logger.exception("Unable to run")
        exit(1)