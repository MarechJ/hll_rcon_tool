"""
    Ported with some tweaks/additions from https://github.com/ElGuillermo/HLL_CRCON_Discord_watch_killrate/blob/main/hll_rcon_tool/custom_tools/watch_killrate.py
"""

import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from logging import getLogger
from time import sleep

import discord
from rcon.api_commands import RconAPI, get_rcon_api
from rcon.cache_utils import invalidates, ttl_cache
from rcon.rcon import SERVER_INFO
from rcon.scoreboard import current_game_stats
from rcon.types import GetDetailedPlayer
from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig
from rcon.user_config.watch_killrate import WatchKillRateUserConfig

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
    "M2 Browning [M3 Half-track]": True,
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
    "M3 Half-track": True,
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
    "M3 Half-track": True,
    "Bedford OYD (Transport)": True,
    "Bedford OYD (Supply)": True,
}


_LAST_REPORTED_CACHE: defaultdict[str, datetime | None] = defaultdict(lambda: None)


def reset_cache():
    global _LAST_REPORTED_CACHE
    with invalidates(get_cache_value):
        _LAST_REPORTED_CACHE = defaultdict(lambda: None)


@ttl_cache(ttl=10, cache_falsy=False)
def get_cache_value(player_id: str) -> datetime | None:
    return _LAST_REPORTED_CACHE[player_id]


def set_cache_value(player_id: str, last_reported: datetime):
    with invalidates(get_cache_value):
        _LAST_REPORTED_CACHE[player_id] = last_reported


def make_embed(
    player_name: str,
    player_id: str,
    timestamp: datetime,
    playtime_secs: int,
    kills: int,
    kpm: float,
    armor_kpm: float,
    artillery_kpm: float,
    mg_kpm: float,
    used_weapons: Counter[str],
    server_name: str,
    author_name: str,
):
    embed = discord.Embed()
    embed.set_author(name=author_name)
    embed.timestamp = timestamp
    embed.add_field(name="Player", value=player_name)
    embed.add_field(name="Player ID", value=player_id)
    embed.add_field(
        name="Playtime", value=timedelta(seconds=playtime_secs), inline=False
    )
    embed.add_field(name="Kills", value=kills, inline=False)
    embed.add_field(name="Overall KPM", value=f"{kpm:.1f}", inline=True)
    if armor_kpm > 0.0:
        embed.add_field(name="Armor KPM", value=f"{armor_kpm:.1f}", inline=False)
    if artillery_kpm > 0.0:
        embed.add_field(
            name="Artillery KPM", value=f"{artillery_kpm:.1f}", inline=False
        )
    if mg_kpm > 0.0:
        embed.add_field(name="MG KPM", value=f"{mg_kpm:.1f}", inline=False)

    embed.add_field(
        name="Weapons",
        value="\n".join(
            f"{weapon}: {kill_count}" for weapon, kill_count in used_weapons.items()
        ),
        inline=False,
    )
    embed.set_footer(text=f"{server_name}")
    return embed


def watch_killrate(api: RconAPI, config: WatchKillRateUserConfig, server_name: str):
    player_stats = current_game_stats()

    if len(player_stats) < 2:
        logger.info("Fewer than 2 players, skipping")
        return

    for player_name, stats in player_stats.items():
        player_id = stats["player_id"]
        for flag in config.whitelist_flags:
            if stats["profile"] and flag in stats["profile"]["flags"]:
                continue

        # There is some wonkiness in player stat calculation and this can be negative sometimes
        playtime_secs: int = (
            int(stats["time_seconds"]) if stats["time_seconds"] > 0 else 0
        )
        kills = stats["kills"]

        if playtime_secs < config.watch_interval_secs:
            logger.debug(
                "Skipping %s/%s did not meet %s minimum play time of %s",
                player_name,
                player_id,
                playtime_secs,
                config.watch_interval_secs,
            )
            continue

        if kills < config.min_kills:
            logger.debug(
                "Skipping %s/%s %s kills < %s minimum kills",
                player_name,
                player_id,
                kills,
                config.min_kills,
            )
            continue

        kpm: float = stats["kills_per_minute"]
        logger.info(f"{player_id} {playtime_secs} {kills} {kpm}")
        used_weapons: Counter = Counter()
        if kpm > min(
            config.killrate_threshold,
            config.killrate_threshold_armor,
            config.killrate_threshold_artillery,
            config.killrate_threshold_mg,
        ):
            timestamp = datetime.now()
            used_weapons = Counter(stats["weapons"])
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
                    if not config.whitelist_armor
                    else 0.0
                ),
                1,
            )
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
                    if not config.whitelist_armor
                    else 0.0
                ),
                1,
            )
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
                    if not config.whitelist_armor
                    else 0.0
                ),
                1,
            )

            if not (
                kpm > config.killrate_threshold
                or armor_kpm > config.killrate_threshold_armor
                or artillery_kpm > config.killrate_threshold_artillery
                or mg_kpm > config.killrate_threshold_mg
            ):
                continue

            # KPM exceeded at this point, make discord embed/log
            last_reported = get_cache_value(player_id)
            if config.only_report_once_per_match and last_reported:
                logger.info(
                    "Already reported (once per match) %s/%s at %s",
                    player_name,
                    player_id,
                    last_reported,
                )
                continue
            elif (
                not last_reported
                or (timestamp - last_reported).total_seconds()
                > config.report_cooldown_mins * 60
            ):
                set_cache_value(player_id, timestamp)
                logger.debug(
                    "Creating embed %s/%s/%s kpm %s armor: %s arty: %s mg: %s",
                    player_name,
                    player_id,
                    used_weapons,
                    kpm,
                    armor_kpm,
                    artillery_kpm,
                    mg_kpm,
                )
                embed: discord.Embed = make_embed(
                    timestamp=timestamp,
                    player_name=player_name,
                    player_id=player_id,
                    kills=kills,
                    playtime_secs=playtime_secs,
                    kpm=kpm,
                    armor_kpm=armor_kpm,
                    artillery_kpm=artillery_kpm,
                    mg_kpm=mg_kpm,
                    used_weapons=used_weapons,
                    server_name=server_name,
                    author_name=config.author,
                )
                for hook in config.webhooks:
                    webhook: discord.SyncWebhook = discord.SyncWebhook.from_url(
                        url=str(hook.url)
                    )
                    role_mentions = " ".join(hook.role_mentions)
                    user_mentions = " ".join(hook.user_mentions)
                    webhook.send(
                        embed=embed, content=f"{user_mentions} {role_mentions}"
                    )
            else:
                logger.info(
                    "Already reported %s/%s at %s",
                    player_name,
                    player_id,
                    last_reported,
                )


def run():
    api: RconAPI = get_rcon_api(SERVER_INFO)
    api.get_detailed_players

    server_config = RconServerSettingsUserConfig.load_from_db()

    while True:
        config = WatchKillRateUserConfig.load_from_db()

        if not config.enabled:
            break

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
