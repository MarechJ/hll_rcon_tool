import logging
import time
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from pydantic import HttpUrl

from rcon.discord import send_to_discord_audit
from rcon.models import PlayerSteamID, PlayerVIP, enter_session
from rcon.rcon import Rcon
from rcon.settings import SERVER_INFO
from rcon.user_config.expired_vips import ExpiredVipsUserConfig
from rcon.utils import INDEFINITE_VIP_DATE, get_server_number

SERVICE_NAME = "ExpiringVIPs"
logger = logging.getLogger(__name__)


def remove_expired_vips(rcon_hook: Rcon, webhook_url: Optional[HttpUrl] = None):
    logger.info(f"Checking for expired VIPs")

    count = 0
    server_number = get_server_number()
    with enter_session() as session:
        expired_vips: List[PlayerVIP] = (
            session.query(PlayerVIP)
            .filter(
                PlayerVIP.server_number == server_number,
                PlayerVIP.expiration < datetime.utcnow(),
            )
            .all()
        )

        count = len(expired_vips)
        for vip in expired_vips:
            name: str
            try:
                name = vip.steamid.names[0].name
            except IndexError:
                name = "No name found"
            message = f"Removing VIP from `{name}`/`{vip.steamid.steam_id_64}` expired `{vip.expiration}`"
            logger.info(message)

            webhookurls: list[HttpUrl | None] | None
            if webhook_url is None:
                webhookurls = None
            else:
                webhookurls = [webhook_url]
            send_to_discord_audit(
                message,
                by=SERVICE_NAME,
                webhookurls=webhookurls,
            )
            rcon_hook.do_remove_vip(vip.steamid.steam_id_64)

        # Look for anyone with VIP but without a record and create one for them
        vip_ids = rcon_hook.get_vip_ids()
        missing_expiration_records = []
        for player in vip_ids:
            player_expiration: datetime | None = player["vip_expiration"]
            if player_expiration is None:
                missing_expiration_records.append(player)
            # Find any old style records that had a floating creation date + 200 year expiration
            # so they get changed to the new fixed UTC 3000-01-01 datetime
            elif (
                player_expiration
                and player_expiration
                >= datetime.now(timezone.utc) + timedelta(days=365 * 100)
                and player_expiration.year < 3000
            ):
                missing_expiration_records.append(player)
                logger.info(
                    "Correcting old style expiration date for %s", player["steam_id_64"]
                )

        for raw_player in missing_expiration_records:
            player: PlayerSteamID = (
                session.query(PlayerSteamID)
                .filter(PlayerSteamID.steam_id_64 == raw_player["steam_id_64"])
                .one_or_none()
            )

            if player:
                expiration_date = INDEFINITE_VIP_DATE
                vip_record = (
                    session.query(PlayerVIP)
                    .filter(
                        PlayerVIP.playersteamid_id == player.id,
                        PlayerVIP.server_number == get_server_number(),
                    )
                    .one_or_none()
                )

                if vip_record:
                    vip_record.expiration = expiration_date
                else:
                    vip_record = PlayerVIP(
                        expiration=expiration_date,
                        playersteamid_id=player.id,
                        server_number=server_number,
                    )
                    session.add(vip_record)

                try:
                    name = player.names[0].name
                except IndexError:
                    name = "No name found"

                logger.info(
                    f"Creating missing VIP expiration (indefinite) record for {name} / {player.steam_id_64}"
                )
            else:
                logger.info(
                    f"{raw_player['steam_id_64']} has VIP on the server but does not have a PlayerSteamID record."
                )

    if count > 0:
        logger.info(f"Removed VIP from {count} player(s)")
    else:
        logger.info("No expired VIPs found")


def run():
    rcon_hook = Rcon(SERVER_INFO)

    while True:
        config = ExpiredVipsUserConfig.load_from_db()

        if config.enabled:
            remove_expired_vips(rcon_hook, config.discord_webhook_url)

        time.sleep(config.interval_minutes * 60)


if __name__ == "__main__":
    run()
