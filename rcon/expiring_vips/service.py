import logging
import time
from datetime import UTC, datetime

from pydantic import HttpUrl

from rcon.discord import send_to_discord_audit
from rcon.models import enter_session
from rcon.rcon import Rcon, get_rcon
from rcon.user_config.expired_vips import ExpiredVipsUserConfig
from rcon.utils import get_server_number
from rcon.vip import get_vip_lists_for_server
from rcon.vip_sync_runner import synchronize_gameserver_vips

SERVICE_NAME = "ExpiringVIPs"
logger = logging.getLogger(__name__)


def remove_expired_vips(
    rcon_hook: Rcon,
    webhook_url: HttpUrl | None = None,
):
    """Deactivate expired VIP List records and synchronize the gameserver."""
    logger.info("Checking for expired VIP List records")

    server_number = get_server_number()
    timestamp = datetime.now(tz=UTC)
    expired_records: list[tuple[str, str, datetime]] = []

    with enter_session() as session:
        vip_lists = get_vip_lists_for_server(
            session,
            server_number=server_number,
        )

        for vip_list in vip_lists:
            for record in vip_list.records:
                if (
                    record.active
                    and record.expires_at is not None
                    and record.expires_at <= timestamp
                ):
                    player_name = (
                        record.player.names[0].name
                        if record.player.names
                        else "No name found"
                    )
                    expired_records.append(
                        (
                            record.player.player_id,
                            player_name,
                            record.expires_at,
                        )
                    )
                    record.active = False

        session.commit()

    webhookurls = None if webhook_url is None else [webhook_url]
    for player_id, player_name, expiration in expired_records:
        message = (
            f"Deactivated expired VIP List record for "
            f"`{player_name}`/`{player_id}` expired `{expiration}`"
        )
        logger.info(message)
        send_to_discord_audit(
            message=message,
            command_name="remove_vip",
            by=SERVICE_NAME,
            webhookurls=webhookurls,
        )

    sync_result = synchronize_gameserver_vips(
        server_number=server_number,
        rcon=rcon_hook,
        timestamp=timestamp,
        dry_run=False,
    )

    if sync_result.execution.successful:
        logger.info(
            "Processed %s expired VIP List record(s)",
            len(expired_records),
        )
    else:
        logger.error(
            "VIP synchronization completed with %s failure(s) after "
            "processing %s expired record(s)",
            len(sync_result.execution.failures),
            len(expired_records),
        )


def run():
    rcon_hook = get_rcon()

    while True:
        config = ExpiredVipsUserConfig.load_from_db()

        if config.enabled:
            remove_expired_vips(rcon_hook, config.discord_webhook_url)

        time.sleep(config.interval_minutes * 60)


if __name__ == "__main__":
    run()
