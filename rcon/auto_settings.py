import logging
import time

from rcon.stats_loop import PlayerCount
from rcon.extended_commands import Rcon
from rcon.settings import SERVER_INFO

logger = logging.getLogger(__name__)

def compare(operand, operator, arguments):
    if operator == 'between':
        start, end = arguments
        return start <= operand <= end
    if operator == 'equals':
        return operand == arguments[0]
    return False


class MetricCondition:

    def __init__(self, name, metric_getter, default_commands):
        self.metric_getter = metric_getter
        self.default_commands = default_commands
        self.name = name
        
    def run_commands(self, rcon, commands):
        for command, params in commands:
            # TODO it might be better to use the API however this process is not aware of it
            try:
                logger.info("Applying %s %s", command, params)
                rcon.__getattribute__(command)(**params)
            except:
                logger.exception('Unable to apply %s %s', command, params)
            time.sleep(10) # go easy on the server

    def apply(self, rcon):
        rules = [
            ('between', (0, 10), [
                ('set_idle_autokick_time', {'minutes': 9999}),
                ('set_autobalance_threshold', {'max_diff': 0}),
                ('set_max_ping_autokick', {'max_ms': 1000}),
                ('set_team_switch_cooldown', {'minutes': 0}),
            ]),
            ('between', (10, 20), [
                ('set_idle_autokick_time', {'minutes': 9999}),
                ('set_autobalance_threshold', {'max_diff': 0}),
                ('set_max_ping_autokick', {'max_ms': 700}),
                ('set_team_switch_cooldown', {'minutes': 5}),
            ]),
            ('between', (20, 50), [
                ('set_idle_autokick_time', {'minutes': 120}),
                ('set_autobalance_threshold', {'max_diff': 1}),
                ('set_max_ping_autokick', {'max_ms': 600}),
                ('set_team_switch_cooldown', {'minutes': 10}),
            ]),
            ('between', (50, 70), [
                ('set_idle_autokick_time', {'minutes': 60}),
                ('set_autobalance_threshold', {'max_diff': 2}),
                ('set_max_ping_autokick', {'max_ms': 500}),
                ('set_team_switch_cooldown', {'minutes': 15}),
            ]),
            ('between', (70, 96), [
                ('set_idle_autokick_time', {'minutes': 20}),
                ('set_autobalance_threshold', {'max_diff': 2}),
                ('set_max_ping_autokick', {'max_ms': 500}),
                ('set_team_switch_cooldown', {'minutes': 30}),
                ('set_vip_slots_num', {'num': 0}),
            ]),
            ('between', (96, 100), [
                ('set_idle_autokick_time', {'minutes': 10}),
                ('set_autobalance_threshold', {'max_diff': 0}),
                ('set_max_ping_autokick', {'max_ms': 500}),
                ('set_team_switch_cooldown', {'minutes': 30}),
                ('set_vip_slots_num', {'num': 1}),
            ]),
        ]
        
        # Todo impllement throttling in here and make it configurable
        for comparator, arguments, commands in rules:
            metric = self.metric_getter()
            if compare(metric, comparator, arguments):
                logger.info("Apply rule for %s %s %s", self.name, comparator, arguments)
                self.run_commands(rcon, commands)
                return # Don't run other rules

        logger.info("Applying default rule for %s", self.name)
        return self.run_commands(rcon, self.default_commands)
        

def run():
    rcon = Rcon(SERVER_INFO)
    conditions = [MetricCondition(
        'player_count',
        lambda: PlayerCount().get_last()[1],
        default_commands=[('set_idle_autokick_time', {'minutes': 10}),
                ('set_autobalance_threshold', {'max_diff': 2}),
                ('set_max_ping_autokick', {'max_ms': 500}),
                ('set_team_switch_cooldown', {'minutes': 15})]
    )]

    while True:
        for c in conditions:
            c.apply(rcon)
        time.sleep(60 * 3)


if __name__ == "__main__":
    run()