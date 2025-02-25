"""
    Ported with some tweaks/additions from https://github.com/ElGuillermo/HLL_CRCON_Discord_watch_killrate/blob/main/hll_rcon_tool/custom_tools/watch_killrate.py
"""

import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from logging import getLogger
from time import sleep

from discord_webhook import DiscordEmbed, DiscordWebhook

from rcon.api_commands import get_rcon_api, RconAPI
from rcon.cache_utils import invalidates, ttl_cache
from rcon.player_history import get_player_profile, player_has_flag
from rcon.player_stats import current_game_stats
from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig
from rcon.user_config.watch_killrate import WatchKillRateUserConfig
from rcon.utils import get_server_number
from rcon.webhook_service import (
    WebhookMessage,
    WebhookMessageType,
    WebhookType,
    enqueue_message,
)

logger = getLogger(__name__)

# TODO: move these to a common location and get translations from T17
# sourced from https://gist.github.com/timraay/5634d85eab552b5dfafb9fd61273dc52#playerinfo-player_name
ARTILLERY: dict[str, bool] = {
    "155MM HOWITZER [M114]": True,
    "150MM HOWITZER [sFH 18]": True,
    "122MM HOWITZER [M1938 (M-30)]": True,
    "QF 25-POUNDER [QF 25-Pounder]": True,
}

MGS: dict[str, bool] = {
    "BROWNING M1919": True,
    "MG34": True,
    "MG42": True,
    "DP-27": True,
    "Lewis Gun": True,
}

ARMOR: dict[str, bool] = {
    "M6 37mm [M8 Greyhound]": True,
    "COAXIAL M1919 [M8 Greyhound]": True,
    "37MM CANNON [Stuart M5A1]": True,
    "COAXIAL M1919 [Stuart M5A1]": True,
    "HULL M1919 [Stuart M5A1]": True,
    "75MM CANNON [Sherman M4A3(75)W]": True,
    "COAXIAL M1919 [Sherman M4A3(75)W]": True,
    "HULL M1919 [Sherman M4A3(75)W]": True,
    "75MM M3 GUN [Sherman M4A3E2]": True,
    "COAXIAL M1919 [Sherman M4A3E2]": True,
    "HULL M1919 [Sherman M4A3E2]": True,
    "76MM M1 GUN [Sherman M4A3E2(76)]": True,
    "COAXIAL M1919 [Sherman M4A3E2(76)]": True,
    "HULL M1919 [Sherman M4A3E2(76)]": True,
    "M2 Browning [M3 Half-track]": True,
    "50mm KwK 39/1 [Sd.Kfz.234 Puma]": True,
    "COAXIAL MG34 [Sd.Kfz.234 Puma]": True,
    "20MM KWK 30 [Sd.Kfz.121 Luchs]": True,
    "COAXIAL MG34 [Sd.Kfz.121 Luchs]": True,
    "75MM CANNON [Sd.Kfz.161 Panzer IV]": True,
    "COAXIAL MG34 [Sd.Kfz.161 Panzer IV]": True,
    "HULL MG34 [Sd.Kfz.161 Panzer IV]": True,
    "75MM CANNON [Sd.Kfz.171 Panther]": True,
    "COAXIAL MG34 [Sd.Kfz.171 Panther]": True,
    "HULL MG34 [Sd.Kfz.171 Panther]": True,
    "88 KWK 36 L/56 [Sd.Kfz.181 Tiger 1]": True,
    "COAXIAL MG34 [Sd.Kfz.181 Tiger 1]": True,
    "HULL MG34 [Sd.Kfz.181 Tiger 1]": True,
    "MG 42 [Sd.Kfz 251 Half-track]": True,
    "19-K 45MM [BA-10]": True,
    "COAXIAL DT [BA-10]": True,
    "45MM M1937 [T70]": True,
    "COAXIAL DT [T70]": True,
    "76MM ZiS-5 [T34/76]": True,
    "COAXIAL DT [T34/76]": True,
    "HULL DT [T34/76]": True,
    "D-5T 85MM [IS-1]": True,
    "COAXIAL DT [IS-1]": True,
    "HULL DT [IS-1]": True,
    "QF 2-POUNDER [Daimler]": True,
    "COAXIAL BESA [Daimler]": True,
    "QF 2-POUNDER [Tetrarch]": True,
    "COAXIAL BESA [Tetrarch]": True,
    "37MM CANNON [M3 Stuart Honey]": True,
    "COAXIAL M1919 [M3 Stuart Honey]": True,
    "HULL M1919 [M3 Stuart Honey]": True,
    "OQF 75MM [Cromwell]": True,
    "COAXIAL BESA [Cromwell]": True,
    "HULL BESA [Cromwell]": True,
    "OQF 57MM [Crusader Mk.III]": True,
    "COAXIAL BESA [Crusader Mk.III]": True,
    "QF 17-POUNDER [Firefly]": True,
    "COAXIAL M1919 [Firefly]": True,
    "OQF 57MM [Churchill Mk.III]": True,
    "COAXIAL BESA 7.92mm [Churchill Mk.III]": True,
    "HULL BESA 7.92mm [Churchill Mk.III]": True,
    "OQF 57MM [Churchill Mk.VII]": True,
    "COAXIAL BESA 7.92mm [Churchill Mk.VII]": True,
    "HULL BESA 7.92mm [Churchill Mk.VII]": True,
    "M8 Greyhound": True,
    "Stuart M5A1": True,
    "Sherman M4A3(75)W": True,
    "Sherman M4A3E2": True,
    "Sherman M4A3E2(76)": True,
    "M3 Half-track": True,
    "GMC CCKW 353 (Transport)": True,
    "GMC CCKW 353 (Supply)": True,
    "Jeep Willys": True,
    "Sd.Kfz.234 Puma": True,
    "Sd.Kfz.121 Luchs": True,
    "Sd.Kfz.161 Panzer IV": True,
    "Sd.Kfz.181 Tiger 1": True,
    "Sd.Kfz.171 Panther": True,
    "Sd.Kfz 251 Half-track": True,
    "Opel Blitz (Transport)": True,
    "Opel Blitz (Supply)": True,
    "Kubelwagen": True,
    "BA-10": True,
    "T70": True,
    "T34/76": True,
    "IS-1 ": True,
    "ZIS-5 (Transport)": True,
    "ZIS-5 (Supply)": True,
    "GAZ-67": True,
    "Daimler": True,
    "Tetrarch": True,
    "M3 Stuart Honey": True,
    "Cromwell": True,
    "Crusader Mk.III": True,
    "Firefly": True,
    "Churchill Mk.III": True,
    "Churchill Mk.VII": True,
    "Bedford OYD (Transport)": True,
    "Bedford OYD (Supply)": True,
}


_LAST_REPORTED_CACHE: defaultdict[str, datetime | None] = defaultdict(lambda: None)


def reset_cache() -> None:
    """Reset cache"""
    global _LAST_REPORTED_CACHE
    with invalidates(get_cache_value):
        _LAST_REPORTED_CACHE = defaultdict(lambda: None)


@ttl_cache(ttl=10, cache_falsy=False)
def get_cache_value(player_id: str) -> datetime | None:
    """Get cache value"""
    return _LAST_REPORTED_CACHE[player_id]


def set_cache_value(player_id: str, last_reported: datetime) -> None:
    """Set cache value"""
    with invalidates(get_cache_value):
        _LAST_REPORTED_CACHE[player_id] = last_reported


def make_embed(
    timestamp: datetime,
    pretty_map_name: str,
    player_name: str,
    player_id: str,
    player_level: int,
    role: str,
    loadout: str,
    playtime_secs: int,
    kills: int,
    kpm: float,
    filtered_kpm: float,
    armor_kpm: float,
    artillery_kpm: float,
    mg_kpm: float,
    used_weapons: Counter[str],
    server_name: str,
    author_name: str,
):
    """Prepare Discord message embed"""
    embed = DiscordEmbed()
    embed.set_author(name=author_name)
    embed.timestamp = str(timestamp)
    embed.add_embed_field(name="Current Match", value=pretty_map_name, inline=False)
    embed.add_embed_field(name="Player", value=player_name)
    embed.add_embed_field(name="Player ID", value=player_id)
    embed.add_embed_field(name="Player Level", value=str(player_level))
    embed.add_embed_field(name="Class", value=role, inline=False)
    embed.add_embed_field(name="Loadout", value=loadout)
    embed.add_embed_field(
        name="Playtime", value=str(timedelta(seconds=playtime_secs)), inline=False
    )
    embed.add_embed_field(name="Kills", value=str(kills), inline=False)
    embed.add_embed_field(name="Overall KPM", value=f"{kpm:.1f}", inline=False)
    embed.add_embed_field(
        name="KPM w/o Armor/Artillery/MGs", value=f"{filtered_kpm:.1f}", inline=False
    )
    if armor_kpm > 0.0:
        embed.add_embed_field(name="Armor KPM", value=f"{armor_kpm:.1f}", inline=False)
    if artillery_kpm > 0.0:
        embed.add_embed_field(
            name="Artillery KPM", value=f"{artillery_kpm:.1f}", inline=False
        )
    if mg_kpm > 0.0:
        embed.add_embed_field(name="MG KPM", value=f"{mg_kpm:.1f}", inline=False)
    embed.add_embed_field(
        name="Weapons",
        value="\n".join(
            f"{weapon}: {kill_count}" for weapon, kill_count in used_weapons.items()
        ),
        inline=False,
    )
    embed.set_footer(text=f"{server_name}")
    return embed


def watch_killrate(
    api: RconAPI, config: WatchKillRateUserConfig, server_name: str
) -> None:
    """Observe all players and report them if they hit k/r thresholds"""
    player_stats: dict = current_game_stats()

    # Allow us to check if a weapon is any of ARMOR or ARTILLERY or MGS
    # so that we can track a base KPM rate that doesn't include any of these
    # because we track those KPMs separately.
    not_base_weapons: dict[str, bool] = {} | ARMOR | ARTILLERY | MGS

    if len(player_stats) < 2:
        logger.info("Fewer than 2 players, skipping")
        return

    for player_name, stats in player_stats.items():
        player_id: str = stats["player_id"]

        # Skip whitelisted players
        whitelisted: bool = False
        for flag in config.whitelist_flags:
            if player_has_flag((get_player_profile(player_id, 0)), flag):
                logger.info("Skipping %s/%s - Whitelist flag", player_name, player_id)
                whitelisted = True
                break
        if whitelisted:
            continue

        # There is some wonkiness in player stat calculation and this can be negative sometimes
        playtime_secs: int = (
            int(stats["time_seconds"]) if stats["time_seconds"] > 0 else 0
        )

        # Skip players with less than minimum playtime
        if playtime_secs < config.watch_interval_secs:
            logger.debug(
                "Skipping %s/%s - Did not meet minimum play time %s/%s",
                player_name,
                player_id,
                playtime_secs,
                config.watch_interval_secs,
            )
            continue

        kills: int = stats["kills"]

        # Skip players with less than minimum kills
        if kills < config.min_kills:
            logger.debug(
                "Skipping %s/%s - Did not meet minimum kills %s/%s",
                player_name,
                player_id,
                kills,
                config.min_kills,
            )
            continue

        kpm: float = stats["kills_per_minute"]
        used_weapons: Counter = Counter()
        # If the players unfiltered KPM doesn't meet any of the thresholds
        # skip all the calculations because this is the highest possible KPM
        # filtering weapons can only reduce KPM
        if kpm > min(
            config.killrate_threshold,
            config.killrate_threshold_armor,
            config.killrate_threshold_artillery,
            config.killrate_threshold_mg,
        ):
            timestamp = datetime.now()
            used_weapons = Counter(stats["weapons"])

            # TODO: redo this section so we aren't looping over used_weapons 4 different times
            # Recalculate the players KPM after filtering out any weapon that is tracked
            # under a specific category (armor, artillery, mgs)
            # So we can avoid triggerings when a specific category has a KPM > than the base rate
            # For instance a killrate threshold of 2.0 and arilltery threshold of 4.0
            filtered_kpm: float = round(
                (
                    (
                        sum(
                            kill_count
                            for weapon, kill_count in used_weapons.items()
                            if weapon not in not_base_weapons
                        )
                        / playtime_secs
                        * 60
                    )
                ),
                2,
            )

            # Armor
            armor_kpm: float = round(
                (
                    (
                        sum(
                            kill_count
                            for weapon, kill_count in used_weapons.items()
                            if weapon in ARMOR
                        )
                        / playtime_secs
                        * 60
                    )
                    if not config.ignore_armor
                    else 0.0
                ),
                2,
            )

            # Artillery
            artillery_kpm: float = round(
                (
                    (
                        sum(
                            kill_count
                            for weapon, kill_count in used_weapons.most_common()
                            if weapon in ARTILLERY
                        )
                        / playtime_secs
                        * 60
                    )
                    if not config.ignore_artillery
                    else 0.0
                ),
                2,
            )

            # Machineguns
            mg_kpm: float = round(
                (
                    (
                        sum(
                            kill_count
                            for weapon, kill_count in used_weapons.items()
                            if weapon in MGS
                        )
                        / playtime_secs
                        * 60
                    )
                    if not config.ignore_mg
                    else 0.0
                ),
                2,
            )

            # Don't make the embed unless at least one condition is met
            # If a category is whitelisted its KPM is set to 0.0
            conditions_met = any(
                [
                    filtered_kpm >= config.killrate_threshold,
                    armor_kpm >= config.killrate_threshold_armor,
                    artillery_kpm >= config.killrate_threshold_artillery,
                    mg_kpm >= config.killrate_threshold_mg,
                ]
            )

            if not conditions_met:
                continue

            # Threshold exceeded

            # Only report once per match if configured
            last_reported = get_cache_value(player_id)
            if config.only_report_once_per_match and last_reported:
                logger.info(
                    "Already reported (once per match) %s/%s at %s",
                    player_name,
                    player_id,
                    last_reported,
                )
                continue

            # Player has not been reported or cooldown has passed
            if (
                not last_reported
                or (timestamp - last_reported).total_seconds()
                > config.report_cooldown_mins * 60
            ):
                set_cache_value(player_id, timestamp)

                logger.info(
                    "Creating embed %s/%s playtime_secs=%s kills=%s kpm=%s, filtered_kpm=%s, armor_kpm=%s, arty_kpm=%s, mg_kpm=%s, %s",
                    player_name,
                    player_id,
                    kpm,
                    filtered_kpm,
                    armor_kpm,
                    artillery_kpm,
                    mg_kpm,
                    used_weapons,
                )

                try:
                    detailed_info = api.get_detailed_player_info(
                        player_name=player_name
                    )
                    player_level: int = detailed_info["level"]
                    player_role: str = detailed_info["role"]
                    player_loadout: str = detailed_info["loadout"]
                except Exception:
                    logger.warning(
                        "Unable to retrieve detailed playerinfo for %s", player_name
                    )
                    player_level: int = 0
                    player_role = "Unknown"
                    player_loadout = "Unknown"

                try:
                    gamestate = api.get_gamestate()
                    map_name = gamestate["current_map"]["pretty_name"]
                except Exception:
                    logger.warning("Unable to retrieve current game state")
                    map_name = "Unknown"

                embed: DiscordEmbed = make_embed(
                    timestamp=timestamp,
                    pretty_map_name=map_name,
                    player_name=player_name,
                    player_id=player_id,
                    player_level=player_level,
                    role=player_role,
                    loadout=player_loadout,
                    kills=kills,
                    playtime_secs=playtime_secs,
                    kpm=kpm,
                    filtered_kpm=filtered_kpm,
                    armor_kpm=armor_kpm,
                    artillery_kpm=artillery_kpm,
                    mg_kpm=mg_kpm,
                    used_weapons=used_weapons,
                    server_name=server_name,
                    author_name=config.author,
                )

                for hook in config.webhooks:
                    wh = DiscordWebhook(url=str(hook.url))
                    wh.add_embed(embed)
                    role_mentions = " ".join(hook.role_mentions)
                    user_mentions = " ".join(hook.user_mentions)
                    wh.content = f"{user_mentions} {role_mentions}"
                    enqueue_message(
                        message=WebhookMessage(
                            payload=wh.json,
                            webhook_type=WebhookType.DISCORD,
                            message_type=WebhookMessageType.ADMIN_PING,
                            server_number=int(get_server_number()),
                        )
                    )

            else:
                logger.info(
                    "Already reported %s/%s at %s, playtime_secs=%s kills=%s kpm=%s, filtered_kpm=%s, armor_kpm=%s, arty_kpm=%s, mg_kpm=%s, %s",
                    player_name,
                    player_id,
                    last_reported,
                    kpm,
                    filtered_kpm,
                    armor_kpm,
                    artillery_kpm,
                    mg_kpm,
                    used_weapons,
                )


def run() -> None:
    """Main process (loop)"""
    api = get_rcon_api()

    while True:
        server_config = RconServerSettingsUserConfig.load_from_db()
        config = WatchKillRateUserConfig.load_from_db()

        if not config.enabled:
            break  # The service will gracefully exit

        watch_killrate(
            api=api,
            config=config,
            server_name=server_config.short_name,
        )
        logger.info("Sleeping %s seconds", config.watch_interval_secs)
        sleep(config.watch_interval_secs)


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        logger.error("Watch KillRate stopped")
        logger.exception(e)
        sys.exit(1)
