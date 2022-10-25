import logging
import time
from datetime import datetime
from dateutil import relativedelta
from typing import Optional

from pydantic import BaseModel, ValidationError, conint

from rcon.config import get_config
from rcon.discord import send_to_discord_audit
from rcon.models import PlayerVIP, enter_session, PlayerSteamID
from rcon.recorded_commands import RecordedRcon
from rcon.settings import SERVER_INFO

SERVICE_NAME = "ExpiringVIPs"
logger = logging.getLogger(__name__)


class ExpiringVIPConfig(BaseModel):
    enabled: bool
    interval: conint(ge=0)
    discord_webhook_url: str


def remove_expired_vips(rcon_hook: RecordedRcon, webhookurl: Optional[str] = None):
    logger.info(f"Checking for expired VIPs")

    count = 0
    with enter_session() as session:
        expired_vips = (
            session.query(PlayerVIP)
            .filter(PlayerVIP.expiration < datetime.utcnow())
            .all()
        )

        count = len(expired_vips)
        for vip in expired_vips:
            name: str
            try:
                name = vip.steamid.names[0].name
            except:
                name = "No name found"
            message = f"Removing VIP from `{name}`/`{vip.steamid.steam_id_64}` expired `{vip.expiration}`"
            logger.info(message)
            send_to_discord_audit(message, by=SERVICE_NAME, webhookurl=webhookurl)
            rcon_hook.do_remove_vip(vip.steamid.steam_id_64)

        # Look for anyone with VIP but without a record and create one for them
        vip_ids = rcon_hook.get_vip_ids()
        missing_expiration_records = [
            player for player in vip_ids if player["vip_expiration"] is None
        ]
        for raw_player in missing_expiration_records:
            player: PlayerSteamID = (
                session.query(PlayerSteamID)
                .filter(PlayerSteamID.steam_id_64 == raw_player["steam_id_64"])
                .one_or_none()
            )

            if player:
                expiration_date = datetime.utcnow() + relativedelta.relativedelta(
                    years=200
                )
                vip_record = PlayerVIP(
                    expiration=expiration_date, playersteamid_id=None
                )
                player.vip = vip_record

                logger.info(
                    f"Creating missing VIP expiration (indefinite) record for {player.name} / {player.steam_id_64}"
                )
            else:
                logger.info(
                    f"{raw_player['steam_id_64']} has VIP on the server but does not have a PlayerSteamID record."
                )

    if count > 0:
        logger.info(f"Removed VIP from {count} players")
    else:
        logger.info("No expired VIPs found")


def run():
    rcon_hook = RecordedRcon(SERVER_INFO)

    try:
        config = get_config()
        config = ExpiringVIPConfig(**config["REMOVE_EXPIRED_VIPS"])
    except ValidationError as e:
        logger.exception(
            f"Invalid REMOVE_EXPIRED_VIPS config {str(e)} check your config/config.yml"
        )
        raise

    while True and config.enabled:
        remove_expired_vips(rcon_hook, config.discord_webhook_url)
        time.sleep(config.interval * 60)
