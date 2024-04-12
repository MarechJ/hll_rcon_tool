import logging

from rcon.models import enter_session
from rcon.user_config import auto_settings
from rcon.user_config.auto_broadcast import AutoBroadcastUserConfig
from rcon.user_config.auto_kick import AutoVoteKickUserConfig
from rcon.user_config.auto_mod_level import AutoModLevelUserConfig
from rcon.user_config.auto_mod_no_leader import AutoModNoLeaderUserConfig
from rcon.user_config.auto_mod_seeding import AutoModSeedingUserConfig
from rcon.user_config.auto_mod_solo_tank import AutoModNoSoloTankUserConfig
from rcon.user_config.ban_tk_on_connect import BanTeamKillOnConnectUserConfig
from rcon.user_config.camera_notification import CameraNotificationUserConfig
from rcon.user_config.chat_commands import ChatCommandsUserConfig
from rcon.user_config.expired_vips import ExpiredVipsUserConfig
from rcon.user_config.gtx_server_name import GtxServerNameChangeUserConfig
from rcon.user_config.log_line_webhooks import LogLineWebhookUserConfig
from rcon.user_config.log_stream import LogStreamUserConfig
from rcon.user_config.name_kicks import NameKickUserConfig
from rcon.user_config.rcon_connection_settings import RconConnectionSettingsUserConfig
from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig
from rcon.user_config.real_vip import RealVipUserConfig
from rcon.user_config.scorebot import ScorebotUserConfig
from rcon.user_config.standard_messages import (
    StandardBroadcastMessagesUserConfig,
    StandardPunishmentMessagesUserConfig,
    StandardWelcomeMessagesUserConfig,
)
from rcon.user_config.steam import SteamUserConfig
from rcon.user_config.vac_game_bans import VacGameBansUserConfig
from rcon.user_config.vote_map import VoteMapUserConfig
from rcon.user_config.webhooks import (
    AdminPingWebhooksUserConfig,
    AuditWebhooksUserConfig,
    CameraWebhooksUserConfig,
    ChatWebhooksUserConfig,
    KillsWebhooksUserConfig,
    WatchlistWebhooksUserConfig,
)

logger = logging.getLogger(__name__)


def seed_default_config():
    logger.info("Seeding DB")
    try:
        with enter_session() as sess:
            auto_settings.AutoSettingsConfig().seed_db(sess)
            AdminPingWebhooksUserConfig.seed_db(sess)
            AuditWebhooksUserConfig.seed_db(sess)
            AutoBroadcastUserConfig.seed_db(sess)
            AutoModLevelUserConfig.seed_db(sess)
            AutoModNoLeaderUserConfig.seed_db(sess)
            AutoModNoSoloTankUserConfig.seed_db(sess)
            AutoModSeedingUserConfig.seed_db(sess)
            AutoVoteKickUserConfig.seed_db(sess)
            BanTeamKillOnConnectUserConfig.seed_db(sess)
            CameraNotificationUserConfig.seed_db(sess)
            CameraWebhooksUserConfig.seed_db(sess)
            ChatCommandsUserConfig.seed_db(sess)
            ChatWebhooksUserConfig.seed_db(sess)
            ExpiredVipsUserConfig.seed_db(sess)
            GtxServerNameChangeUserConfig.seed_db(sess)
            KillsWebhooksUserConfig.seed_db(sess)
            LogLineWebhookUserConfig.seed_db(sess)
            LogStreamUserConfig.seed_db(sess)
            NameKickUserConfig.seed_db(sess)
            RconConnectionSettingsUserConfig.seed_db(sess)
            RconServerSettingsUserConfig.seed_db(sess)
            RealVipUserConfig.seed_db(sess)
            ScorebotUserConfig.seed_db(sess)
            StandardBroadcastMessagesUserConfig.seed_db(sess)
            StandardPunishmentMessagesUserConfig.seed_db(sess)
            StandardWelcomeMessagesUserConfig.seed_db(sess)
            SteamUserConfig.seed_db(sess)
            VacGameBansUserConfig.seed_db(sess)
            VoteMapUserConfig.seed_db(sess)
            WatchlistWebhooksUserConfig.seed_db(sess)

    except Exception as e:
        logger.exception("Failed to seed DB")


if __name__ == "__main__":
    seed_default_config()
