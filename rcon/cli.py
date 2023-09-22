import inspect
import json
import logging
import sys
from datetime import datetime, timedelta
from typing import Any, Set, Type

import click
import pydantic
import yaml

import rcon.expiring_vips.service
import rcon.user_config
import rcon.user_config.utils
from rcon import auto_settings, broadcast, game_logs, routines
from rcon.automods import automod
from rcon.cache_utils import RedisCached, get_redis_pool
from rcon.game_logs import LogLoop
from rcon.models import install_unaccent
from rcon.rcon_ import Rcon
from rcon.scoreboard import live_stats_loop
from rcon.server_stats import (
    save_server_stats_for_last_hours,
    save_server_stats_since_inception,
)
from rcon.settings import SERVER_INFO
from rcon.steam_utils import enrich_db_users
from rcon.user_config.user_config import seed_default_config
from rcon.user_config.webhooks import (
    BaseMentionWebhookUserConfig,
    BaseWebhookUserConfig,
)
from rcon.utils import ApiKey

logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


ctl = Rcon(SERVER_INFO)


@cli.command(name="live_stats_loop")
def run_stats_loop():
    try:
        live_stats_loop()
    except KeyboardInterrupt:
        sys.exit(0)
    except:
        logger.exception("Stats loop stopped")
        sys.exit(1)


@cli.command(name="record_server_stats_inception")
def save_stats():
    save_server_stats_since_inception()


@cli.command(name="record_server_stats")
def save_recent_stats():
    save_server_stats_for_last_hours()


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


@cli.command(name="deprecated_log_loop")
def run_logs_eventloop():
    game_logs.event_loop()


@cli.command(name="broadcast_loop")
def run_broadcast_loop():
    broadcast.run()


@cli.command(name="auto_settings")
def auto_settings_loop():
    auto_settings.run()


@cli.command(name="routines")
def run_routines():
    routines.run()


@cli.command(name="expiring_vips")
def run_expiring_vips():
    rcon.expiring_vips.service.run()


@cli.command(name="automod")
def run_automod():
    automod.run()


@cli.command(name="log_recorder")
@click.option("-t", "--frequency-min", default=5)
@click.option("-n", "--now", is_flag=True)
def run_log_recorder(frequency_min, now):
    game_logs.LogRecorder(frequency_min, now).run()


def init(force=False):
    # init_db(force)
    install_unaccent()
    seed_default_config()


@cli.command(name="init_db")
@click.option("--force", default=False, is_flag=True)
def do_init(force):
    init(force)


@cli.command(name="set_maprotation")
@click.argument("maps", nargs=-1)
def maprot(maps):
    ctl.set_maprotation(list(maps))


@cli.command(name="register_api")
def register():
    ApiKey().generate_key()


@cli.command(name="unregister_api")
def unregister():
    ApiKey().delete_key()


@cli.command(name="import_vips")
@click.argument("file", type=click.File("r"))
@click.option("-p", "--prefix", default="")
def importvips(file, prefix):
    for line in file:
        line = line.strip()
        steamid, name = line.split(" ", 1)
        ctl.do_add_vip(name=f"{prefix}{name}", steam_id_64=steamid)


@cli.command(name="clear_cache")
def clear():
    RedisCached.clear_all_caches(get_redis_pool())


@cli.command
def export_vips():
    print("/n".join(f"{d['steam_id_64']} {d['name']}" for d in ctl.get_vip_ids()))


def do_print(func):
    def wrap(*args, **kwargs):
        from pprint import pprint

        res = func(*args, **kwargs)
        pprint(res)
        return res

    return wrap


@cli.command(name="reprocess-games")
@click.argument("start_day_offset", type=int)
@click.option(
    "--end-day-offset",
    type=int,
    default=0,
    help="The number of days relative to now at which you want the reprocessing to end. For example if you set 1, the reprocessing will stop at yesterday",
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Set this flag if you want the existing stats to be overriden. Otherwise they will just log an error and we move on to the next",
)
def process_games(start_day_offset, end_day_offset=0, force=False):
    from sqlalchemy import and_
    from sqlalchemy.exc import IntegrityError

    from rcon.models import Maps, enter_session
    from rcon.workers import record_stats_from_map

    start_date = datetime.now() - timedelta(days=start_day_offset)
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = datetime.now() - timedelta(days=end_day_offset)
    end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999)

    print("Reprocessing date range: ", start_date, end_date)
    with enter_session() as sess:
        all_maps = (
            sess.query(Maps)
            .filter(and_(Maps.start > start_date, Maps.start < end_date))
            .all()
        )
        print("Found %s games to reprocess" % len(all_maps))
        for map_ in all_maps:
            print("Reprocessing map: ", map_.to_dict())
            try:
                record_stats_from_map(sess, map_, dict(), force=force)
                sess.commit()
                print("Done")
            except IntegrityError as e:
                sess.rollback()
                # logger.exception("Failed")
                print(
                    "Can't re-process stats. Probably already exist. Set force flag to override. Error msg: ",
                    repr(e),
                )
                continue


@cli.command(name="set_user_settings")
@click.argument("input", type=click.Path())
@click.option(
    "--type", "file_type", type=str, default="yaml", help="File format (JSON or YAML)"
)
@click.option("--dry-run", type=bool, default=True, help="Validate settings only")
def set_user_settings(input: click.Path, file_type="yaml", dry_run=True):
    ALLOWED_TYPES = ("JSON", "YAML", "YML")
    if file_type.upper() not in ALLOWED_TYPES:
        raise ValueError(f"{file_type} must be one of {ALLOWED_TYPES}")

    keys_to_exclude = set(
        [BaseWebhookUserConfig.KEY(), BaseMentionWebhookUserConfig.__name__]
    )

    keys_to_models = {
        model.KEY_NAME: model
        for model in rcon.user_config.utils.all_subclasses(
            rcon.user_config.utils.BaseUserConfig
        )
        if model.KEY_NAME not in keys_to_exclude
    }

    user_settings: dict[str, Any]
    if file_type.upper() == "JSON":
        with open(str(input)) as fp:
            print(f"parsing JSON {input}")
            try:
                user_settings = json.load(fp)
            except json.decoder.JSONDecodeError as e:
                logger.error("JSON decoding error:")
                logger.error(e)
                sys.exit(-1)
    else:
        with open(str(input)) as fp:
            print(f"parsing YAML {input}")
            try:
                user_settings = yaml.safe_load_all(fp)
                # pprint(dict(user_settings))
            except yaml.YAMLError as e:
                logger.error("YAML decoding error:")
                logger.error(e)
                sys.exit(-1)

    for key in user_settings.keys():
        if key not in keys_to_models:
            logger.error(f"{key} not an allowed key, no changes made.")
            sys.exit(-1)

    parsed_models: list[rcon.user_config.utils.BaseUserConfig] = []
    model: rcon.user_config.utils.BaseUserConfig
    for key, payload in user_settings.items():
        cls = keys_to_models[key]
        print(f"Parsing {key} as {cls}")
        try:
            model = cls(**payload)
        except pydantic.ValidationError as e:
            logger.error(e)
            sys.exit(-1)

        parsed_models.append(model)

    if not dry_run:
        for model in parsed_models:
            rcon.user_config.utils.set_user_config(model.KEY(), model.model_dump())


PREFIXES_TO_EXPOSE = ["get_", "set_", "do_"]
EXCLUDED: Set[str] = {"set_maprotation", "connection_pool"}

# Dynamically register all the methods from ServerCtl
# use dir instead of inspect.getmembers to avoid touching cached_property
# members that would be initialized even if we want to skip them, like connection_pool
for name in dir(ctl):
    if name in EXCLUDED:
        continue

    func = getattr(ctl, name)

    if (
        not any(name.startswith(prefix) for prefix in PREFIXES_TO_EXPOSE)
        or name in EXCLUDED
    ):
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

if __name__ == "__main__":
    cli()
