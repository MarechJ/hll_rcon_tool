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
from rcon.cache_utils import RedisCached, get_redis_pool, invalidates
from rcon.discord_chat import get_handler
from rcon.game_logs import LogLoop, load_generic_hooks
from rcon.models import enter_session, install_unaccent
from rcon.rcon_ import Rcon
from rcon.scoreboard import live_stats_loop
from rcon.server_stats import (
    save_server_stats_for_last_hours,
    save_server_stats_since_inception,
)
from rcon.settings import SERVER_INFO
from rcon.steam_utils import enrich_db_users
from rcon.user_config.auto_settings import AutoSettingsConfig, seed_default_config
from rcon.user_config.webhooks import (
    BaseMentionWebhookUserConfig,
    BaseUserConfig,
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
    # Invalidate the cache on startup so it always loads user settings
    # since they might have been set through the CLI, etc.
    with invalidates(load_generic_hooks, get_handler):
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


def _models_to_exclude():
    """Return model classes that do not map directly to a user config"""
    # Any sort of parent class that doesn't directly map to a user config
    # should be excluded
    return set(
        [
            BaseWebhookUserConfig.__name__,
            BaseMentionWebhookUserConfig.__name__,
            BaseUserConfig.__name__,
        ]
    )


@cli.command(name="get_user_settings")
@click.argument("server", type=int)
@click.argument("output", type=click.Path())
@click.option(
    "--output-server",
    type=int,
    default=None,
    help="The server number to export for (if different)",
)
def get_user_setting(server: int, output: click.Path, output_server=None):
    """Dump all user settings for SERVER to OUTPUT file.

    SERVER: The server number (SERVER_NUMBER as set in the compose files).

    Only configured settings are dumped, never defaults.
    """
    if output_server is None:
        output_server = server

    key_format = "{server}_{cls_name}"

    keys_to_models: dict[str, BaseUserConfig] = {
        model.__name__: model
        for model in rcon.user_config.utils.all_subclasses(BaseUserConfig)
    }

    # Since a CRCON install can have multiple servers, but get_server_number()
    # depends on the environment, pass the server number to the tool
    dump: dict[str, Any] = {}
    for model in keys_to_models.values():
        key = key_format.format(server=server, cls_name=model.__name__)
        output_key = key_format.format(server=output_server, cls_name=model.__name__)
        value = rcon.user_config.utils.get_user_config(key)
        if value:
            config = model.model_validate(value)
            dump[output_key] = config.model_dump()

    # Auto settings are unique right now
    auto_settings_key = f"{server}_auto_settings"
    auto_settings_output_key = f"{output_server}_auto_settings"
    auto_settings_model = rcon.user_config.utils.get_user_config(
        f"{server}_auto_settings"
    )
    if auto_settings_model:
        dump[auto_settings_output_key] = auto_settings_model

    with open(str(output), "w") as fp:
        fp.write((json.dumps(dump, indent=2)))

    print("Done")


@cli.command(name="set_user_settings")
@click.argument("server", type=int)
@click.argument("input", type=click.Path())
@click.option("--dry-run", type=bool, default=True, help="Validate settings only")
def set_user_settings(server: int, input: click.Path, dry_run=True):
    """Set all (specified) user settings for SERVER from INPUT file.

    if DRY_RUN is not false, it will only validate the file.
    No settings will be set unless the entire file validates correctly.*

    *Auto settings are not validated

    SERVER: The server number (SERVER_NUMBER as set in the compose files).
    """
    # Auto settings are unique right now
    auto_settings_key = f"{server}_auto_settings"

    if dry_run:
        print(f"{dry_run=} validating models only, not setting")

    config_models: dict[str, Type[BaseUserConfig]] = {
        rcon.user_config.utils.USER_CONFIG_KEY_FORMAT.format(
            server=server, cls_name=model.__name__
        ): model
        for model in rcon.user_config.utils.all_subclasses(BaseUserConfig)
        if model.__name__ not in _models_to_exclude()
    }

    user_settings: dict[str, Any]
    with open(str(input)) as fp:
        print(f"parsing {input=}")
        try:
            user_settings = json.load(fp)
        except json.decoder.JSONDecodeError as e:
            logger.error("JSON decoding error:")
            logger.error(e)
            sys.exit(-1)

    for key in user_settings.keys():
        if key not in config_models and key != auto_settings_key:
            logger.error(f"{key} not an allowed key, no changes made.")
            sys.exit(-1)

    parsed_models: list[tuple[Type[BaseUserConfig], BaseUserConfig]] = []
    model: BaseUserConfig
    for key, payload in user_settings.items():
        if key == auto_settings_key:
            continue

        cls = config_models[key]
        try:
            model = cls(**payload)
            print(f"Successfully parsed {key} as {cls}")
        except pydantic.ValidationError as e:
            logger.error(e)
            sys.exit(-1)

        parsed_models.append((cls, model))

    if not dry_run:
        for cls, model in parsed_models:
            key = rcon.user_config.utils.USER_CONFIG_KEY_FORMAT.format(
                server=server, cls_name=cls.__name__
            )
            print(f"setting {key=} class={cls.__name__}")
            rcon.user_config.utils.set_user_config(key, model.model_dump())

        if auto_settings_key in user_settings:
            rcon.user_config.utils.set_user_config(
                auto_settings_key, user_settings[auto_settings_key]
            )

    print("Done")


@cli.command(name="reset_user_settings")
@click.argument("server", type=int)
def reset_user_settings(server: int):
    """Reset all user settings for SERVER to their defaults.

    There is no way to undo this if you do not save your settings in advance!

    SERVER: The server number (SERVER_NUMBER as set in the compose files).
    """
    with enter_session() as sess:
        AutoSettingsConfig().reset_settings(sess)
        sess.commit()

    models: list[Type[BaseUserConfig]] = [
        model
        for model in rcon.user_config.utils.all_subclasses(BaseUserConfig)
        if model.__name__ not in _models_to_exclude()
    ]

    for cls in models:
        model = cls()
        key = rcon.user_config.utils.USER_CONFIG_KEY_FORMAT.format(
            server=server, cls_name=cls.__name__
        )
        print(f"Resetting {key}")
        rcon.user_config.utils.set_user_config(key, model.model_dump())

    print("Done")


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
