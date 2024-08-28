import inspect
import json
import logging
import sys
from datetime import datetime, timedelta
from typing import Any, Set, Type

import click
import pydantic
import yaml
from sqlalchemy import func as pg_func
from sqlalchemy import select, text, update

import rcon.expiring_vips.service
import rcon.user_config
import rcon.user_config.utils
from rcon import auto_settings, broadcast, game_logs, routines
from rcon.automods import automod
from rcon.blacklist import BlacklistCommandHandler
from rcon.cache_utils import RedisCached, get_redis_pool, invalidates
from rcon.discord_chat import get_handler
from rcon.game_logs import LogLoop, LogStream, load_generic_hooks
from rcon.models import PlayerID, enter_session, install_unaccent
from rcon.rcon import get_rcon
from rcon.scoreboard import live_stats_loop
from rcon.server_stats import (
    save_server_stats_for_last_hours,
    save_server_stats_since_inception,
)
from rcon.settings import SERVER_INFO
from rcon.steam_utils import enrich_db_users
from rcon.user_config.auto_settings import AutoSettingsConfig
from rcon.user_config.log_stream import LogStreamUserConfig
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
    except Exception as e:
        logger.exception("DB users enrichment stopped: %s", e)
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


@cli.command(name="log_stream")
def run_log_stream():
    try:
        config = LogStreamUserConfig.load_from_db()
        stream = LogStream()
        stream.clear()
        if config.enabled:
            stream.run()
    except:
        logger.exception("Log stream stopped")
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


@cli.command(name="blacklists")
def run_blacklists():
    BlacklistCommandHandler().run()


@cli.command(name="log_recorder")
@click.option("-t", "--frequency-min", default=5)
@click.option("-n", "--now", is_flag=True)
def run_log_recorder(frequency_min, now):
    game_logs.LogRecorder(frequency_min, now).run()


def init(force=False):
    install_unaccent()


@cli.command(name="init_db")
@click.option("--force", default=False, is_flag=True)
def do_init(force):
    init(force)


@cli.command(name="set_maprotation")
@click.argument("maps", nargs=-1)
def maprot(maps):
    ctl = get_rcon()
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
    ctl = get_rcon()
    for line in file:
        line = line.strip()
        player_id, name = line.split(" ", 1)
        ctl.add_vip(player_id=player_id, description=f"{prefix}{name}")


@cli.command(name="clear_cache")
def clear():
    RedisCached.clear_all_caches(get_redis_pool())


@cli.command
def export_vips():
    ctl = get_rcon()
    print("/n".join(f"{d['player_id']} {d['name']}" for d in ctl.get_vip_ids()))


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
            rcon.user_config.utils.set_user_config(key, model)

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
        rcon.user_config.utils.set_user_config(key, model)

    print("Done")


def _merge_duplicate_player_ids(existing_ids: set[str] | None = None):
    players = {}

    with enter_session() as session:
        if existing_ids:
            stmt = select(PlayerID).filter(PlayerID.player_id.in_(existing_ids))
        else:
            stmt = select(PlayerID)
        rows = session.execute(stmt).scalars()

        for player in rows:
            id_, steamid = player.id, player.player_id

            if steamid in players:
                players[steamid].append(id_)
            else:
                players[steamid] = [id_]

        duplicate_players = dict(filter(lambda p: len(p[1]) > 1, players.items()))
        for steamid, ids in duplicate_players.items():
            logger.info(f"Merging {steamid}")
            keep = ids.pop(0)

            session.execute(
                text(
                    "UPDATE blacklist_record SET player_id_id = :keep WHERE player_id_id = ANY(:ids)"
                ),
                {"keep": keep, "ids": ids},
            )
            session.execute(
                text(
                    "UPDATE log_lines SET player1_steamid = :keep WHERE player1_steamid = ANY(:ids)"
                ),
                {"keep": keep, "ids": ids},
            )
            session.execute(
                text(
                    "UPDATE log_lines SET player2_steamid = :keep WHERE player2_steamid = ANY(:ids)"
                ),
                {"keep": keep, "ids": ids},
            )
            session.execute(
                text(
                    "UPDATE player_at_count SET playersteamid_id = :keep WHERE playersteamid_id = ANY(:ids)"
                ),
                {"keep": keep, "ids": ids},
            )
            session.execute(
                text(
                    "UPDATE player_blacklist SET playersteamid_id = :keep WHERE playersteamid_id = ANY(:ids)"
                ),
                {"keep": keep, "ids": ids},
            )
            session.execute(
                text(
                    "UPDATE player_comments SET playersteamid_id = :keep WHERE playersteamid_id = ANY(:ids)"
                ),
                {"keep": keep, "ids": ids},
            )
            session.execute(
                text(
                    "UPDATE player_flags SET playersteamid_id = :keep WHERE playersteamid_id = ANY(:ids)"
                ),
                {"keep": keep, "ids": ids},
            )
            session.execute(
                text(
                    "UPDATE player_optins SET playersteamid_id = :keep WHERE playersteamid_id = ANY(:ids)"
                ),
                {"keep": keep, "ids": ids},
            )
            session.execute(
                text(
                    "UPDATE player_sessions SET playersteamid_id = :keep WHERE playersteamid_id = ANY(:ids)"
                ),
                {"keep": keep, "ids": ids},
            )
            session.execute(
                text(
                    "UPDATE player_stats SET playersteamid_id = :keep WHERE playersteamid_id = ANY(:ids)"
                ),
                {"keep": keep, "ids": ids},
            )
            session.execute(
                text(
                    "UPDATE player_vip SET playersteamid_id = :keep WHERE playersteamid_id = ANY(:ids)"
                ),
                {"keep": keep, "ids": ids},
            )
            session.execute(
                text(
                    "UPDATE player_watchlist SET playersteamid_id = :keep WHERE playersteamid_id = ANY(:ids)"
                ),
                {"keep": keep, "ids": ids},
            )
            session.execute(
                text(
                    "UPDATE players_actions SET playersteamid_id = :keep WHERE playersteamid_id = ANY(:ids)"
                ),
                {"keep": keep, "ids": ids},
            )
            session.execute(
                text("DELETE FROM steam_info WHERE playersteamid_id = ANY(:ids)"),
                {"ids": ids},
            )
            session.execute(
                text("DELETE FROM player_names WHERE playersteamid_id = ANY(:ids)"),
                {"ids": ids},
            )
            session.execute(
                text("DELETE FROM steam_id_64 WHERE id = ANY(:ids)"), {"ids": ids}
            )


@cli.command(name="merge_duplicate_player_ids")
def merge_duplicate_player_ids():
    logger.info(f"Merging duplicate player ID records")
    _merge_duplicate_player_ids()
    logger.info(f"Duplicate player ID merge complete")


@cli.command(name="convert_win_player_ids")
def convert_win_player_ids():
    player_ids_to_merge: set[str] = set()
    updated = 0
    # .values(player_id=pg_func.md5(PlayerID.player_id))
    with enter_session() as session:
        logger.info(f"Converting old style windows store player IDs to new style")
        old_style_stmt = select(PlayerID).filter(PlayerID.player_id.like("%-%"))
        old_style_rows = session.execute(old_style_stmt).scalars()

        for p in old_style_rows:
            logger.info(f"updating {p.player_id}")
            already_exists_stmt = select(PlayerID).filter(
                PlayerID.player_id == pg_func.md5(p.player_id)
            )
            res = session.execute(already_exists_stmt).one_or_none()
            if res:
                logger.info(f"{p.player_id} already has a converted ID")
                player_ids_to_merge.add(p.player_id)
            else:
                p.player_id = pg_func.md5(p.player_id)

        logger.info(f"Converted {updated} player IDs")

    if player_ids_to_merge:
        logger.info(
            f"{len(player_ids_to_merge)} old style player IDs already existed, merging them"
        )
        _merge_duplicate_player_ids(existing_ids=player_ids_to_merge)


PREFIXES_TO_EXPOSE = ["get_", "set_", "do_"]
EXCLUDED: Set[str] = {"set_maprotation", "connection_pool"}

# For this to work correctly with click it has to be at the top level of the module and ran on import
ctl = get_rcon()
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
