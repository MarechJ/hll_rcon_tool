import inspect
import logging
import click
import sys
import time

from rcon.settings import SERVER_INFO
from rcon.utils import ApiKey
from rcon.extended_commands import Rcon
from rcon import game_logs, broadcast, stats_loop, auto_settings, routines
from rcon.game_logs import LogLoop
from rcon.models import init_db, install_unaccent
from rcon.user_config import seed_default_config
from rcon.cache_utils import RedisCached, get_redis_pool
from rcon.scoreboard import live_stats_loop
from rcon.steam_utils import enrich_db_users

logger = logging.getLogger(__name__)

@click.group()
def cli():
    pass

ctl = Rcon(
    SERVER_INFO
)

@cli.command(name="live_stats_loop")
def run_stats_loop():
    try:
        live_stats_loop()
    except:
        logger.exception("Stats loop stopped")
        sys.exit(1)


@cli.command(name="enrich_db_users")
def run_enrich_db_users():
    try:
        enrich_db_users()
    except:
        logger.exception("DB users enrichment stopped")
        sys.exit(1)


@cli.command(name="log_loop")
def run_log_loop():
    try:
        LogLoop().run()
    except:
        logger.exception("Chat recorder stopped")
        sys.exit(1)


@cli.command(name='deprecated_log_loop')
def run_logs_eventloop():
    game_logs.event_loop()


@cli.command(name='broadcast_loop')
def run_broadcast_loop():
    broadcast.run()


@cli.command(name='auto_settings')
def auto_settings_loop():
    auto_settings.run()


@cli.command(name='routines')
def run_routines():
    routines.run()


@cli.command(name='log_recorder')
@click.option('-t', '--frequency-min', default=5)
@click.option('-n', '--now', is_flag=True)
def run_log_recorder(frequency_min, now):
    game_logs.LogRecorder(frequency_min, now).run()


def init(force=False):
    #init_db(force)
    install_unaccent()
    seed_default_config()


@cli.command(name="init_db")
@click.option('--force', default=False, is_flag=True)
def do_init(force):
    init(force)


@cli.command(name="set_maprotation")
@click.argument('maps', nargs=-1)
def maprot(maps):
    ctl.set_maprotation(list(maps))


@cli.command(name="register_api")
def register():
    ApiKey().generate_key()


@cli.command(name="unregister_api")
def unregister():
    ApiKey().delete_key()


@cli.command(name="import_vips")
@click.argument('file', type=click.File('r'))
@click.option('-p', '--prefix', default='')
def importvips(file, prefix):
    for line in file:
        line = line.strip()
        steamid, name = line.split(' ', 1)
        ctl.do_add_vip(name=f'{prefix}{name}', steam_id_64=steamid)


@cli.command(name="clear_cache")
def clear():
    RedisCached.clear_all_caches(get_redis_pool())

@cli.command
def export_vips():
    print("/n".join(f"{d['steam_id_64']} {d['name']}" for d in  ctl.get_vip_ids()))

def do_print(func):
    def wrap(*args, **kwargs):
        res = func(*args, **kwargs)
        print(res)
        return res
    return wrap


PREFIXES_TO_EXPOSE = [
    'get_', 'set_', 'do_'
]

EXCLUDED = {
    'set_maprotation'
}

# Dynamically register all the methods from ServerCtl
for name, func in inspect.getmembers(ctl):
    if not any(name.startswith(prefix) for prefix in PREFIXES_TO_EXPOSE) or name in EXCLUDED:
        continue
    wrapped = do_print(func)

    # Registering the arguments of the function must be done from last
    # to first as they are decorators
    for pname, param in [i for i in inspect.signature(func).parameters.items()][::-1]:
        if param.default != inspect._empty:
            wrapped = click.option(f"--{pname}", pname, default=param.default)(wrapped)
        else:
            wrapped = click.argument(pname)(wrapped)

    cli.command(name=name)(wrapped)


if __name__ == '__main__':
    cli()
