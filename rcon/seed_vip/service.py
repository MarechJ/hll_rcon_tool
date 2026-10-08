import sys
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from logging import getLogger
from time import sleep

import discord
import humanize

from rcon.api_commands import get_rcon_api
from rcon.seed_vip.utils import (
    calc_vip_expiration_timestamp,
    collect_steam_ids,
    get_gamestate,
    get_next_player_bucket,
    get_online_players,
    get_vips,
    is_seeded,
    make_seed_announcement_embed,
    message_players,
    resolve_reward_vip_list,
    reward_players,
)
from rcon.user_config.seed_vip import SeedVIPUserConfig

logger = getLogger(__name__)

DRY_RUN_DISCORD_PREFIX = (
    "🧪 **DRY RUN – SIMULATION**\nNo VIPs or in-game reward messages will be sent.\n\n"
)


def format_discord_message(message: str, dry_run: bool) -> str:
    return f"{DRY_RUN_DISCORD_PREFIX}{message}" if dry_run else message


def run():
    config = SeedVIPUserConfig.load_from_db()
    current_lang = config.language

    rcon_api = get_rcon_api()

    to_add_vip_steam_ids: set[str] = set()
    no_reward_steam_ids: set[str] = set()
    player_name_lookup: dict[str, str] = {}
    prev_announced_bucket: int = 0
    player_buckets = config.player_announce_thresholds
    if player_buckets:
        next_player_bucket = player_buckets[0]
    else:
        next_player_bucket = None
    last_bucket_announced = False
    seeded_timestamp: datetime | None = None

    gamestate = get_gamestate(rcon=rcon_api)
    is_seeding = not is_seeded(config=config, gamestate=gamestate)

    try:
        while True:
            # Reload the config each loop to catch changes to the config
            config = SeedVIPUserConfig.load_from_db()

            if not config.enabled:
                logger.info("Seed VIP is not enabled")
                break

            try:
                if current_lang != config.language:
                    logger.info(f"Deactivating language={current_lang}")
                    humanize.deactivate()

                if config.language:
                    # The language to translate to if using the `nice_time_delta` and `nice_expiration_date` settings
                    # Any valid language code shoud work, look here for examples: https://gist.github.com/jacobbubu/1836273
                    current_lang = config.language
                    humanize.activate(config.language)
                    logger.info(f"Activated language={config.language}")
            except FileNotFoundError:
                logger.error(
                    f"Unable to activate language={config.language}, defaulting to English"
                )

            online_players = get_online_players(rcon=rcon_api)
            if online_players is None:
                logger.debug(
                    f"Did not receive a usable result from `get_online_players`, sleeping {config.poll_time_seeding} seconds"
                )
                sleep(config.poll_time_seeding)
                continue

            gamestate = get_gamestate(rcon=rcon_api)

            if gamestate is None:
                logger.debug(
                    f"Did not receive a usable result from `get_gamestate`, sleeping {config.poll_time_seeding} seconds"
                )
                sleep(config.poll_time_seeding)
                continue

            total_players = (
                gamestate["num_allied_players"] + gamestate["num_axis_players"]
            )

            player_name_lookup |= {
                p.player_id: p.name for p in online_players.players.values()
            }

            logger.debug(
                f"{is_seeding=} {len(online_players.players.keys())} online players (`get_players`), {gamestate['num_allied_players']} allied {gamestate['num_axis_players']} axis players (gamestate)",
            )
            to_add_vip_steam_ids = collect_steam_ids(
                config=config,
                players=online_players,
                cum_steam_ids=to_add_vip_steam_ids,
            )

            # Server seeded
            if is_seeding and is_seeded(config=config, gamestate=gamestate):
                st = seeded_timestamp = datetime.now(tz=UTC)
                logger.info(f"Server seeded at {st.isoformat()}")
                # Preserve the full set of qualified players before filtering.
                qualified_player_ids = set(to_add_vip_steam_ids)
                online_player_ids = {
                    player.player_id for player in online_players.players.values()
                }

                # Players who were online when seeded but did not meet the
                # configured requirements. Existing VIPs which qualified are
                # deliberately not included in this group.
                no_reward_steam_ids = online_player_ids - qualified_player_ids

                # get_vip_ids returns the effective VIP state for this server.
                # Any effective VIP is skipped, regardless of its source,
                # expiration, or target list.
                all_vips = get_vips(rcon=rcon_api)
                existing_vip_ids = qualified_player_ids & set(all_vips)
                to_add_vip_steam_ids = qualified_player_ids - existing_vip_ids

                if existing_vip_ids:
                    logger.info(
                        "Skipping %s qualified players with an existing "
                        "effective VIP: %s",
                        len(existing_vip_ids),
                        sorted(existing_vip_ids),
                    )

                expiration_timestamps = defaultdict(
                    lambda time=st, cfg=config: calc_vip_expiration_timestamp(
                        config=cfg,
                        expiration=None,
                        from_time=time,
                    )
                )

                target_vip_list = resolve_reward_vip_list(
                    rcon=rcon_api,
                    config=config,
                )
                rewarded_player_ids: set[str] = set()

                if target_vip_list is not None:
                    rewarded_player_ids = reward_players(
                        rcon=rcon_api,
                        config=config,
                        vip_list_id=int(target_vip_list["id"]),
                        to_add_vip_steam_ids=to_add_vip_steam_ids,
                        current_vips=all_vips,
                        players_lookup=player_name_lookup,
                        expiration_timestamps=expiration_timestamps,
                    )
                elif to_add_vip_steam_ids:
                    logger.error(
                        "Seed VIP rewards were not written because no valid "
                        "target VIP list is available"
                    )

                # Only players whose write succeeded receive a reward message.
                message_players(
                    rcon=rcon_api,
                    config=config,
                    message=config.player_messages.reward_player_message,
                    steam_ids=rewarded_player_ids,
                    expiration_timestamps=expiration_timestamps,
                )

                # Message those who did not earn
                message_players(
                    rcon=rcon_api,
                    config=config,
                    message=config.player_messages.reward_player_message_no_vip,
                    steam_ids=no_reward_steam_ids,
                    expiration_timestamps=None,
                )

                # Post seeding complete Discord message
                if config.hooks:
                    logger.debug(
                        f"Making embed for `{config.player_messages.seeding_complete_message}`"
                    )
                    embed = make_seed_announcement_embed(
                        message=format_discord_message(
                            config.player_messages.seeding_complete_message,
                            config.dry_run,
                        ),
                        current_map=gamestate["current_map"]["pretty_name"],
                        time_remaining=gamestate["raw_time_remaining"],
                        player_count_message=config.player_messages.player_count_message,
                        num_allied_players=gamestate["num_allied_players"],
                        num_axis_players=gamestate["num_axis_players"],
                    )
                    if embed:
                        for wh in config.hooks:
                            wh = discord.SyncWebhook.from_url(url=str(wh.url))
                            wh.send(embed=embed)

                # Reset for next seed
                last_bucket_announced = False
                prev_announced_bucket = 0
                to_add_vip_steam_ids.clear()
                is_seeding = False
            elif (
                not is_seeding
                and not is_seeded(config=config, gamestate=gamestate)
                and total_players > 0
            ):
                delta: timedelta | None = None
                if seeded_timestamp:
                    delta = datetime.now(tz=UTC) - seeded_timestamp

                if not seeded_timestamp:
                    logger.debug(
                        f"Back in seeding: seeded_timestamp={seeded_timestamp} {delta=} {config.requirements.buffer=}"
                    )
                    is_seeding = True
                elif delta and (delta > config.requirements.buffer.as_timedelta):
                    logger.debug(
                        f"Back in seeding: seeded_timestamp={seeded_timestamp.isoformat()} {delta=} delta > buffer {delta > config.requirements.buffer.as_timedelta} {config.requirements.buffer=}"
                    )
                    is_seeding = True
                else:
                    logger.info(
                        f"Delaying seeding mode due to buffer of {config.requirements.buffer} > {delta} time since seeded"
                    )

            if is_seeding:
                sleep_time = config.poll_time_seeding

                # When we fall back into seeding with players still on the
                # server we want to announce the largest bucket possible or
                # it will announce from the smallest to the largest and spam
                # Discord with unneccessary announcements
                next_player_bucket = get_next_player_bucket(
                    config.player_announce_thresholds,
                    total_players=total_players,
                )

                # Announce seeding progress
                logger.debug(
                    f"whs={[wh.url for wh in config.hooks]} {config.player_announce_thresholds=} {total_players=} {prev_announced_bucket=} {next_player_bucket=} {last_bucket_announced=}"
                )
                if (
                    config.hooks
                    and next_player_bucket
                    and not last_bucket_announced
                    and prev_announced_bucket < next_player_bucket
                    and total_players >= next_player_bucket
                ):
                    prev_announced_bucket = next_player_bucket

                    embed = make_seed_announcement_embed(
                        message=format_discord_message(
                            config.player_messages.seeding_in_progress_message.format(
                                player_count=total_players
                            ),
                            config.dry_run,
                        ),
                        current_map=gamestate["current_map"]["pretty_name"],
                        time_remaining=gamestate["raw_time_remaining"],
                        player_count_message=config.player_messages.player_count_message,
                        num_allied_players=gamestate["num_allied_players"],
                        num_axis_players=gamestate["num_axis_players"],
                    )
                    if next_player_bucket == config.player_announce_thresholds[-1]:
                        logger.debug("setting last_bucket_announced=True")
                        last_bucket_announced = True

                    if embed:
                        for wh in config.hooks:
                            wh = discord.SyncWebhook.from_url(url=str(wh.url))
                            wh.send(embed=embed)

            else:
                sleep_time = config.poll_time_seeded

            logger.info(f"sleeping {sleep_time=}")
            sleep(sleep_time)
    except* Exception as eg:
        for e in eg.exceptions:
            logger.exception(e)
        raise


if __name__ == "__main__":
    try:
        run()
    except:  # noqa
        logger.exception("Seed VIP stopped")
        sys.exit(1)
