import functools
import inspect
from collections import defaultdict
from datetime import datetime, timedelta
from logging import getLogger
from typing import Any, Dict, Iterable, Literal, Optional, Sequence, Type

from rcon import blacklist, game_logs, maps, player_history, vip, webhook_service
from rcon.audit import ingame_mods, online_mods
from rcon.cache_utils import RedisCached, get_redis_pool
from rcon.discord import audit_user_config_differences
from rcon.gtx import GTXFtp
from rcon.message_templates import (
    add_message_template,
    delete_message_template,
    edit_message_template,
    get_all_message_templates,
    get_message_template,
    get_message_template_categories,
    get_message_templates,
)
from rcon.models import MessageTemplate, enter_session
from rcon.player_history import (
    add_flag_to_player,
    get_players_by_appearance,
    remove_flag,
    update_player_profile,
)
from rcon.player_stats import TimeWindowStats
from rcon.rcon import Rcon
from rcon.scoreboard import ScoreboardUserConfig
from rcon.settings import SERVER_INFO
from rcon.types import (
    AdminUserType,
    AllMessageTemplateTypes,
    BlacklistSyncMethod,
    BlacklistType,
    BlacklistWithRecordsType,
    GameServerBanType,
    MessageTemplateCategory,
    MessageTemplateType,
    ParsedLogsType,
    PlayerCommentType,
    PlayerFlagType,
    PlayerProfileTypeEnriched,
    ServerInfoType,
    VipListRecordEditType,
    VipListRecordType,
    VipListSyncMethod,
    VipListType,
    VipListTypeWithRecordsType,
    VoteMapStatusType,
)
from rcon.user_config.auto_broadcast import AutoBroadcastUserConfig
from rcon.user_config.auto_kick import AutoVoteKickUserConfig
from rcon.user_config.auto_mod_level import AutoModLevelUserConfig
from rcon.user_config.auto_mod_no_leader import AutoModNoLeaderUserConfig
from rcon.user_config.auto_mod_seeding import AutoModSeedingUserConfig
from rcon.user_config.auto_mod_solo_tank import AutoModNoSoloTankUserConfig
from rcon.user_config.ban_tk_on_connect import BanTeamKillOnConnectUserConfig
from rcon.user_config.camera_notification import CameraNotificationUserConfig
from rcon.user_config.chat_commands import ChatCommandsUserConfig
from rcon.user_config.gtx_server_name import GtxServerNameChangeUserConfig
from rcon.user_config.legacy_scorebot import ScorebotUserConfig
from rcon.user_config.log_line_webhooks import LogLineWebhookUserConfig
from rcon.user_config.log_stream import LogStreamUserConfig
from rcon.user_config.name_kicks import NameKickUserConfig
from rcon.user_config.rcon_chat_commands import RConChatCommandsUserConfig
from rcon.user_config.rcon_connection_settings import RconConnectionSettingsUserConfig
from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig
from rcon.user_config.real_vip import RealVipUserConfig
from rcon.user_config.seed_vip import SeedVIPUserConfig
from rcon.user_config.standard_messages import (
    StandardBroadcastMessagesUserConfig,
    StandardPunishmentMessagesUserConfig,
    StandardWelcomeMessagesUserConfig,
)
from rcon.user_config.steam import SteamUserConfig
from rcon.user_config.utils import BaseUserConfig, validate_user_config
from rcon.user_config.vac_game_bans import VacGameBansUserConfig
from rcon.user_config.vote_map import VoteMapUserConfig
from rcon.user_config.watch_killrate import WatchKillRateUserConfig
from rcon.user_config.webhooks import (
    AdminPingWebhooksUserConfig,
    AuditWebhooksUserConfig,
    CameraWebhooksUserConfig,
    ChatWebhooksUserConfig,
    KillsWebhooksUserConfig,
    WatchlistWebhooksUserConfig,
)
from rcon.utils import MISSING, SERVER_NUMBER, MissingType
from rcon.vote_map import VoteMap
from rcon.watchlist import PlayerWatch

logger = getLogger(__name__)

PLAYER_ID = "player_id"

CTL: Optional["RconAPI"] = None


def parameter_aliases(alias_to_param: Dict[str, str]):
    """Specify parameter aliases of a function. This might be useful to preserve backwards
    compatibility or to handle parameters named after a Python reserved keyword.

    Takes a mapping of aliases to their parameter name."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for alias, param in alias_to_param.items():
                if alias in kwargs:
                    kwargs[param] = kwargs.pop(alias)
            return func(*args, **kwargs)

        wrapper._parameter_aliases = alias_to_param
        return wrapper

    return decorator


def get_rcon_api(credentials: ServerInfoType | None = None) -> "RconAPI":
    """Return a initialized Rcon connection to the game server

    This maintains a single initialized instance across a Python interpreter
    instance unless someone explicitly chooses to use multiple instances.
    This also doesn't automatically attempt to connect to the game server on
    module import.

    Args:
        credentials: A dict of the game server IP, RCON port and RCON password
    """
    global CTL

    if credentials is None:
        credentials = SERVER_INFO

    if CTL is None:
        CTL = RconAPI(credentials)
    return CTL


class RconAPI(Rcon):
    """Defines additional commands so they are usable internally and in auto settings

    These commands are all automatically exposed as API endpoint in rconweb.api.views

    The set_X_config commands are a special case and **kwargs must be included so it will work
    properly with how auto settings passes in parameters
    """

    def __init__(self, *args, pool_size: bool | None = None, **kwargs):
        super().__init__(*args, pool_size=pool_size, **kwargs)

    @staticmethod
    def _validate_user_config(
        command_name: str,
        by: str,
        model: Type[BaseUserConfig],
        data: dict[str, Any] | BaseUserConfig,
        dry_run: bool = True,
        reset_to_default: bool = False,
    ):
        old_model = model.load_from_db()
        res = validate_user_config(
            model=model,
            data=data,
            dry_run=dry_run,
            reset_to_default=reset_to_default,
        )

        if res:
            audit_user_config_differences(
                old_model=old_model,
                new_model=data,
                command_name=command_name,
                author=by,
            )
        return res

    def get_blacklists(self) -> list[BlacklistType]:
        """Get all blacklists.

        Blacklists are collections of ban-like records stored by CRCON
        to provide greater flexibility and scalability.
        """
        with enter_session() as sess:
            return [
                bl.to_dict(with_records=False) for bl in blacklist.get_blacklists(sess)
            ]

    def get_blacklist(self, blacklist_id: int) -> BlacklistWithRecordsType:
        """Get a blacklist and its respective records.

        Blacklists are collections of ban-like records stored by CRCON
        to provide greater flexibility and scalability.

        Args:
            blacklist_id: The ID of the blacklist
        """
        with enter_session() as sess:
            return blacklist.get_blacklist(sess, blacklist_id, strict=True).to_dict(
                with_records=True
            )

    def create_blacklist(
        self,
        name: str,
        sync: BlacklistSyncMethod = BlacklistSyncMethod.KICK_ONLY,
        servers: Sequence[int] | None = None,
    ):
        """
        Creates a new, empty blacklist.

        Blacklists are collections of ban-like records stored by CRCON
        to provide greater flexibility and scalability.

        Args:
            name:
                Name for the list
            sync:
                Method to use for synchronizing an active record with the
                game server. See `BlacklistSyncMethod` for more details.
            servers:
                A sequence of server numbers which this blacklist will
                apply to. `None` means all servers.
        """
        return blacklist.create_blacklist(
            name=name,
            sync=BlacklistSyncMethod(sync.lower()),
            servers=servers,
        )

    def edit_blacklist(
        self,
        blacklist_id: int,
        name: str = MISSING,
        sync_method: BlacklistSyncMethod = MISSING,
        servers: Sequence[int] | None = MISSING,
    ):
        """
        Edits a blacklist.

        Blacklists are collections of ban-like records stored by CRCON
        to provide greater flexibility and scalability.

        Args:
            blacklist_id: The ID of the blacklist
            name: What to name the blacklist
            sync: Method to use for synchronizing records with the game
            servers: List of server numbers this blacklist applies to. `None` means all.
        """
        if sync_method:
            sync_method = BlacklistSyncMethod(sync_method.lower())
        return blacklist.edit_blacklist(
            blacklist_id,
            name=name,
            sync=sync_method,
            servers=servers,
        )

    def delete_blacklist(
        self,
        blacklist_id: int,
    ):
        """
        Removes a blacklist alongside all of its records.

        Blacklists are collections of ban-like records stored by CRCON
        to provide greater flexibility and scalability.

        Args:
            blacklist_id: The ID of the blacklist
        """
        return blacklist.delete_blacklist(blacklist_id)

    def get_blacklist_records(
        self,
        player_id: str = None,
        reason: str = None,
        blacklist_id: int = None,
        exclude_expired: bool = False,
        page_size: int = 50,
        page: int = 1,
    ):
        page_size = int(page_size)
        page = int(page)
        if blacklist_id is not None:
            blacklist_id = int(blacklist_id)
        with enter_session() as sess:
            records, total = blacklist.search_blacklist_records(
                sess,
                player_id=player_id,
                reason=reason,
                blacklist_id=blacklist_id,
                exclude_expired=exclude_expired,
                page_size=page_size,
                page=page,
            )
            return {
                "records": [
                    record.to_dict(with_blacklist=True, with_player=True)
                    for record in records
                ],
                "page": page,
                "page_size": page_size,
                "total": total,
            }

    def add_blacklist_record(
        self,
        player_id: str,
        blacklist_id: int,
        reason: str,
        expires_at: datetime | None = None,
        admin_name: str = "",
    ) -> BlacklistType:
        """
        Adds a new record to a blacklist.

        Blacklists are collections of ban-like records stored by CRCON
        to provide greater flexibility and scalability.

        Args:
            player_id: steam_id_64 or windows store ID to blacklist
            blacklist_id: The ID of the blacklist to use
            reason: The reason the player was blacklisted for
            expires_at: When the blacklist should expire, if ever
            admin_name: The person/tool that is blacklisting the player
        """
        return blacklist.add_record_to_blacklist(
            player_id=player_id,
            blacklist_id=blacklist_id,
            reason=reason,
            expires_at=expires_at,
            admin_name=admin_name,
        )

    def edit_blacklist_record(
        self,
        record_id: int,
        blacklist_id: int = MISSING,
        reason: str = MISSING,
        expires_at: datetime | None = MISSING,
    ) -> bool:
        """
        Edits a blacklist record.

        Blacklists are collections of ban-like records stored by CRCON
        to provide greater flexibility and scalability.

        The blacklisted player ID cannot be edited. You instead need to
        delete this record and create a new one.

        Args:
            record_id: The ID of the record
            blacklist_id: The ID of the blacklist this record should be part of
            reason: The reason the player was blacklisted for
            expires_at: When the blacklist should expire, if ever
        """
        return blacklist.edit_record_from_blacklist(
            record_id,
            blacklist_id=blacklist_id,
            reason=reason,
            expires_at=expires_at,
        )

    def delete_blacklist_record(
        self,
        record_id: int,
    ) -> bool:
        """
        Removes a blacklist record.

        Blacklists are collections of ban-like records stored by CRCON
        to provide greater flexibility and scalability.

        Args:
            record_id: The ID of the record
        """
        return blacklist.remove_record_from_blacklist(record_id)

    def unblacklist_player(self, player_id: str) -> bool:
        """Expires all blacklists of a player and unbans them from all servers.

        Args:
            player_id: steam_id_64 or windows store ID
        """
        blacklist.expire_all_player_blacklists(player_id)
        return True

    def unban(
        self,
        player_id: str,
    ) -> bool:
        """Remove all temporary and permanent bans from the player_id.

        This does not remove any blacklists, meaning the player may be immediately banned
        again. To remove any bans or blacklists, use `unblacklist_player` instead.

        Args:
            player_id: steam_id_64 or windows store ID
        """
        bans = self.get_bans()
        type_to_func = {
            "temp": self.remove_temp_ban,
            "perma": self.remove_perma_ban,
        }
        success = False
        for b in bans:
            if b.get(PLAYER_ID) == player_id:
                success = True
                type_to_func[b["type"]](b["player_id"])

        return success

    def clear_cache(self) -> bool:
        """Clear every key in this servers Redis cache and return number of deleted keys

        Many things in CRCON are cached in Redis to avoid excessively polling
        the game server, this clears the entire cache which is sometimes necessary
        to force a refresh
        """
        # TODO: allow clearing specific cache keys
        return RedisCached.clear_all_caches(get_redis_pool())

    def get_player_profile(
        self,
        player_id: str,
        num_sessions: int = 10,
    ) -> PlayerProfileTypeEnriched | None:
        raw_profile = player_history.get_player_profile(
            player_id=player_id, nb_sessions=num_sessions
        )

        bans: list[GameServerBanType] = []
        comments: list[PlayerCommentType] = []
        profile: PlayerProfileTypeEnriched | None = None
        if raw_profile:
            bans = self.get_ban(player_id=player_id)
            comments = player_history.get_player_comments(player_id=player_id)

            profile = raw_profile.copy()
            profile.update(
                {
                    "bans": bans,
                    "comments": comments,
                }
            )
        return profile

    def get_player_comments(self, player_id: str) -> list[PlayerCommentType]:
        return player_history.get_player_comments(player_id=player_id)

    def post_player_comment(self, player_id: str, comment: str, by: str):
        return player_history.post_player_comment(
            player_id=player_id,
            comment=comment,
            user=by,
        )

    def get_player_messages(self, player_id: str):
        return player_history.get_player_messages(player_id=player_id)

    def get_players_history(
        self,
        page: int = 1,
        page_size: int = 500,
        last_seen_from: datetime | None = None,
        last_seen_till: datetime | None = None,
        player_id: str | None = None,
        player_name: str | None = None,
        blacklisted: bool | None = None,
        is_watched: bool | None = None,
        exact_name_match: bool = False,
        ignore_accent: bool = True,
        flags: str | list[str] | None = None,
        country: str | None = None,
    ):
        return get_players_by_appearance(
            page=page,
            page_size=page_size,
            last_seen_from=last_seen_from,
            last_seen_till=last_seen_till,
            player_name=player_name,
            blacklisted=blacklisted,
            player_id=player_id,
            is_watched=is_watched,
            exact_name_match=exact_name_match,
            ignore_accent=ignore_accent,
            flags=flags,
            country=country,
        )

    def flag_player(
        self,
        player_id: str,
        flag: str,
        player_name: str | None = None,
        comment: str | None = None,
    ) -> PlayerFlagType:
        """Adds a new flag to the specified player_id

        Flags are used to label users and some tools use the flags to whitelist
        users. They are traditionally an emoji (the frontend uses an emoji picker)
        but there is no length restriction in the database.

        Args:
            player_id: steam_id_64 or windows store ID
            player_name: The players name which will be added as an alias
            flag:
            comment:


        """

        player, new_flag = add_flag_to_player(
            player_id=player_id, flag=flag, comment=comment, player_name=player_name
        )
        # TODO: can we preserve discord auditing with player aliases?
        # data["player_name"] = " | ".join(n["name"] for n in player["names"])

        return new_flag

    def unflag_player(
        self,
        flag_id: int | None = None,
        player_id: str | None = None,
        flag: str | None = None,
    ) -> PlayerFlagType:
        """Flags can be removed either by flag_id (database key) or by passing a player ID and flag

        Args:
            flag_id: The database primary key of the flag record to delete
            player_id: steam_id_64 or windows store ID
            flag: The flag to remove from `player_id` if present
        """
        player, removed_flag = remove_flag(
            flag_id=flag_id, player_id=player_id, flag=flag
        )
        return removed_flag

    def set_server_name(self, name: str):
        # TODO: server name won't change until map change
        # but the cache also needs to be cleared, but can't
        # immediately clear or it will just refresh but we
        # can use a timer or clear the cache on match start

        gtx = GTXFtp.from_config()
        gtx.change_server_name(new_name=name)

    @staticmethod
    def toggle_player_watch(
        player_id: str,
        audit_name: str | None,
        add: bool,
        reason: str | None = None,
        player_name: str | None = None,
    ) -> bool:
        watcher = PlayerWatch(player_id=player_id)
        if add:
            result = watcher.watch(
                reason=reason or "",
                by=audit_name,
                player_name=player_name or "",
            )
        else:
            result = watcher.unwatch()

        return result

    def watch_player(
        self,
        player_id: str,
        reason: str,
        by: str,
        player_name: str | None = None,
    ) -> bool:
        return self.toggle_player_watch(
            player_id=player_id,
            player_name=player_name,
            reason=reason,
            audit_name=by,
            add=True,
        )

    def unwatch_player(
        self,
        player_id: str,
    ) -> bool:
        return self.toggle_player_watch(
            player_id=player_id,
            player_name=None,
            reason=None,
            audit_name=None,
            add=False,
        )

    def get_online_mods(self) -> list[AdminUserType]:
        return online_mods()

    def get_ingame_mods(self) -> list[AdminUserType]:
        return ingame_mods()

    @parameter_aliases(
        {
            "from": "from_",
        }
    )
    def get_historical_logs(
        self,
        player_name: str | None = None,
        player_id: str | None = None,
        action: str | None = None,
        limit: int = 1000,
        from_: datetime | None = None,
        till: datetime | None = None,
        time_sort: Literal["desc", "asc"] = "desc",
        exact_player_match: bool = False,
        exact_action: bool = True,
        server_filter: str | None = None,
    ):
        lines = game_logs.get_historical_logs(
            player_name=player_name,
            action=action,
            player_id=player_id,
            limit=limit,
            from_=from_,
            till=till,
            time_sort=time_sort,
            exact_player_match=exact_player_match,
            exact_action=exact_action,
            server_filter=server_filter,
        )

        return lines

    def get_recent_logs(
        self,
        filter_player: list[str] | str = [],
        filter_action: list[str] = [],
        inclusive_filter: bool = True,
        start: int = 0,
        end: int = 10000,
        exact_player_match: bool = True,
        exact_action: bool = False,
    ) -> ParsedLogsType:
        return game_logs.get_recent_logs(
            start=start,
            end=end,
            player_search=filter_player,
            action_filter=filter_action,
            exact_player_match=exact_player_match,
            exact_action=exact_action,
            inclusive_filter=inclusive_filter,
        )

    def get_votemap_status(self) -> list[VoteMapStatusType]:
        v = VoteMap()

        votes = v.get_votes()
        votes_by_map: dict[maps.Layer, list[str]] = defaultdict(list)
        for player, map_ in votes.items():
            votes_by_map[map_].append(player)

        selection = v.get_selection()

        result = []
        for map_ in selection:
            result.append({"map": map_, "voters": votes_by_map[map_]})

        return sorted(result, key=lambda m: len(m["voters"]), reverse=True)

    def reset_votemap_state(self) -> list[VoteMapStatusType]:
        v = VoteMap()
        v.clear_votes()
        v.gen_selection()
        v.apply_results()

        return self.get_votemap_status()

    def get_votemap_whitelist(self) -> list[str]:
        v = VoteMap()

        # TODO: update this when we return `Layer`s instead of strings
        return [str(map) for map in v.get_map_whitelist()]

    def add_map_to_votemap_whitelist(self, map_name: str):
        v = VoteMap()
        v.add_map_to_whitelist(map_name=map_name)

    def add_maps_to_votemap_whitelist(self, map_names: Iterable[str]):
        v = VoteMap()
        v.add_maps_to_whitelist(map_names=map_names)

    def remove_map_from_votemap_whitelist(self, map_name: str):
        v = VoteMap()
        v.remove_map_from_whitelist(map_name=map_name)

    def remove_maps_from_votemap_whitelist(self, map_names: Iterable[str]):
        v = VoteMap()
        v.remove_maps_from_whitelist(map_names=map_names)

    def reset_map_votemap_whitelist(self):
        v = VoteMap()
        v.reset_map_whitelist()

    def set_votemap_whitelist(self, map_names: Iterable[str]):
        v = VoteMap()
        v.set_map_whitelist(map_names=map_names)

    def get_votemap_config(self) -> VoteMapUserConfig:
        return VoteMapUserConfig.load_from_db()

    def validate_votemap_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            by=by,
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            model=VoteMapUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def set_votemap_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        old_config = VoteMapUserConfig.load_from_db()

        res = self._validate_user_config(
            by=by,
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            model=VoteMapUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

        new_config = VoteMapUserConfig.load_from_db()

        # on -> off or off -> on
        if old_config.enabled != new_config.enabled:
            self.reset_votemap_state()

        return True

    def get_auto_broadcasts_config(self) -> AutoBroadcastUserConfig:
        return AutoBroadcastUserConfig.load_from_db()

    def validate_auto_broadcasts_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=AutoBroadcastUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def set_auto_broadcasts_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=AutoBroadcastUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def get_votekick_autotoggle_config(self) -> AutoVoteKickUserConfig:
        return AutoVoteKickUserConfig.load_from_db()

    def validate_votekick_autotoggle_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=AutoVoteKickUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def set_votekick_autotoggle_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=AutoVoteKickUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def get_auto_mod_level_config(self) -> AutoModLevelUserConfig:
        return AutoModLevelUserConfig.load_from_db()

    def validate_auto_mod_level_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=AutoModLevelUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def set_auto_mod_level_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=AutoModLevelUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def get_auto_mod_no_leader_config(self) -> AutoModNoLeaderUserConfig:
        return AutoModNoLeaderUserConfig.load_from_db()

    def validate_auto_mod_no_leader_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=AutoModNoLeaderUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def set_auto_mod_no_leader_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=AutoModNoLeaderUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def get_auto_mod_seeding_config(self) -> AutoModSeedingUserConfig:
        return AutoModSeedingUserConfig.load_from_db()

    def validate_auto_mod_seeding_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=AutoModSeedingUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def set_auto_mod_seeding_config(
        self,
        by: str,
        user_config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=AutoModSeedingUserConfig,
            data=user_config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def get_auto_mod_solo_tank_config(self) -> AutoModNoSoloTankUserConfig:
        return AutoModNoSoloTankUserConfig.load_from_db()

    def validate_auto_mod_solo_tank_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=AutoModNoSoloTankUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def set_auto_mod_solo_tank_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=AutoModNoSoloTankUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def get_tk_ban_on_connect_config(self) -> BanTeamKillOnConnectUserConfig:
        return BanTeamKillOnConnectUserConfig.load_from_db()

    def validate_tk_ban_on_connect_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=BanTeamKillOnConnectUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def set_tk_ban_on_connect_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=BanTeamKillOnConnectUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def get_real_vip_config(
        self,
    ) -> RealVipUserConfig:
        return RealVipUserConfig.load_from_db()

    def validate_real_vip_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=RealVipUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def set_real_vip_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=RealVipUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def get_seed_vip_config(
        self,
    ) -> SeedVIPUserConfig:
        return SeedVIPUserConfig.load_from_db()

    def validate_seed_vip_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=SeedVIPUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def set_seed_vip_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=SeedVIPUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def get_camera_notification_config(self) -> CameraNotificationUserConfig:
        return CameraNotificationUserConfig.load_from_db()

    def set_camera_notification_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=CameraNotificationUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def validate_camera_notification_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=CameraNotificationUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def get_server_name_change_config(self) -> GtxServerNameChangeUserConfig:
        return GtxServerNameChangeUserConfig.load_from_db()

    def set_server_name_change_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=GtxServerNameChangeUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def validate_server_name_change_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=GtxServerNameChangeUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def get_log_line_webhook_config(self) -> LogLineWebhookUserConfig:
        return LogLineWebhookUserConfig.load_from_db()

    def set_log_line_webhook_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=LogLineWebhookUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def validate_log_line_webhook_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=LogLineWebhookUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def get_name_kick_config(self) -> NameKickUserConfig:
        return NameKickUserConfig.load_from_db()

    def set_name_kick_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=NameKickUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def validate_name_kick_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=NameKickUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def get_rcon_connection_settings_config(self) -> RconConnectionSettingsUserConfig:
        return RconConnectionSettingsUserConfig.load_from_db()

    def set_rcon_connection_settings_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=RconConnectionSettingsUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def validate_rcon_connection_settings_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=RconConnectionSettingsUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def get_rcon_server_settings_config(self) -> RconServerSettingsUserConfig:
        return RconServerSettingsUserConfig.load_from_db()

    def set_rcon_server_settings_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=RconServerSettingsUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def validate_rcon_server_settings_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=RconServerSettingsUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    # TODO: legacy remove this in a few releases
    def get_scorebot_config(self) -> ScorebotUserConfig:
        return ScorebotUserConfig.load_from_db()

    def get_scoreboard_config(self) -> ScoreboardUserConfig:
        return ScoreboardUserConfig.load_from_db()

    def set_scoreboard_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=ScoreboardUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def validate_scoreboard_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=ScoreboardUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def get_standard_broadcast_messages(self) -> StandardBroadcastMessagesUserConfig:
        return StandardBroadcastMessagesUserConfig.load_from_db()

    def set_standard_broadcast_messages(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=StandardBroadcastMessagesUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def validate_standard_broadcast_messages(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=StandardBroadcastMessagesUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def get_standard_punishments_messages(self) -> StandardPunishmentMessagesUserConfig:
        return StandardPunishmentMessagesUserConfig.load_from_db()

    def set_standard_punishments_messages(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=StandardPunishmentMessagesUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def validate_standard_punishments_messages(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=StandardPunishmentMessagesUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def get_standard_welcome_messages(self) -> StandardWelcomeMessagesUserConfig:
        return StandardWelcomeMessagesUserConfig.load_from_db()

    def set_standard_welcome_messages(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=StandardWelcomeMessagesUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def validate_standard_welcome_messages(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=StandardWelcomeMessagesUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def get_steam_config(self) -> SteamUserConfig:
        return SteamUserConfig.load_from_db()

    def set_steam_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=SteamUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def validate_steam_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=SteamUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def get_vac_game_bans_config(self) -> VacGameBansUserConfig:
        return VacGameBansUserConfig.load_from_db()

    def set_vac_game_bans_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=VacGameBansUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def validate_vac_game_bans_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=VacGameBansUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def get_admin_pings_discord_webhooks_config(self) -> AdminPingWebhooksUserConfig:
        return AdminPingWebhooksUserConfig.load_from_db()

    def set_admin_pings_discord_webhooks_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=AdminPingWebhooksUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def validate_admin_pings_discord_webhooks_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=AdminPingWebhooksUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def get_audit_discord_webhooks_config(self) -> AuditWebhooksUserConfig:
        return AuditWebhooksUserConfig.load_from_db()

    def set_audit_discord_webhooks_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=AuditWebhooksUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def validate_audit_discord_webhooks_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=AuditWebhooksUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def get_camera_discord_webhooks_config(self) -> CameraWebhooksUserConfig:
        return CameraWebhooksUserConfig.load_from_db()

    def set_camera_discord_webhooks_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=CameraWebhooksUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def validate_camera_discord_webhooks_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=CameraWebhooksUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def get_chat_discord_webhooks_config(self) -> ChatWebhooksUserConfig:
        return ChatWebhooksUserConfig.load_from_db()

    def set_chat_discord_webhooks_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=ChatWebhooksUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def validate_chat_discord_webhooks_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=ChatWebhooksUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def get_kills_discord_webhooks_config(self):
        return KillsWebhooksUserConfig.load_from_db()

    def set_kills_discord_webhooks_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            by=by,
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            model=KillsWebhooksUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def validate_kills_discord_webhooks_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=KillsWebhooksUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def get_watchlist_discord_webhooks_config(self) -> WatchlistWebhooksUserConfig:
        return WatchlistWebhooksUserConfig.load_from_db()

    def set_watchlist_discord_webhooks_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=WatchlistWebhooksUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def validate_watchlist_discord_webhooks_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=WatchlistWebhooksUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def get_chat_commands_config(self):
        return ChatCommandsUserConfig.load_from_db()

    def set_chat_commands_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=ChatCommandsUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def validate_chat_commands_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=ChatCommandsUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def get_rcon_chat_commands_config(self):
        return RConChatCommandsUserConfig.load_from_db()

    def set_rcon_chat_commands_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=RConChatCommandsUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def validate_rcon_chat_commands_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=RConChatCommandsUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def get_log_stream_config(self):
        return LogStreamUserConfig.load_from_db()

    def set_log_stream_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=LogStreamUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def validate_log_stream_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=LogStreamUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def get_watch_killrate_config(self):
        return WatchKillRateUserConfig.load_from_db()

    def set_watch_killrate_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=WatchKillRateUserConfig,
            data=config or kwargs,
            dry_run=False,
            reset_to_default=reset_to_default,
        )

    def validate_watch_killrate_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=WatchKillRateUserConfig,
            data=config or kwargs,
            dry_run=True,
            reset_to_default=reset_to_default,
        )

    def get_date_scoreboard(self, start: int, end: int):
        try:
            start_date = datetime.fromtimestamp(int(start))
        except (ValueError, KeyError, TypeError) as e:
            logger.error(e)
            start_date = datetime.now() - timedelta(minutes=60)
        try:
            end_date = datetime.fromtimestamp(int(end))
        except (ValueError, KeyError, TypeError) as e:
            logger.error(e)
            end_date = datetime.now()

        stats = TimeWindowStats()

        try:
            result = stats.get_players_stats_at_time(start_date, end_date)
        except Exception as e:
            logger.exception("Unable to produce date stats: %s", e)
            result = {}

        return result

    def get_objective_row(self, row: int):
        return super().get_objective_row(int(row))

    def get_message_templates(
        self, category: MessageTemplateCategory
    ) -> list[MessageTemplateType]:
        """Get all possible message type categories"""
        return get_message_templates(category=category)

    def get_message_template_categories(self) -> list[MessageTemplateCategory]:
        return get_message_template_categories()

    def get_message_template(self, id: int) -> MessageTemplateType | None:
        """Return the message template for the specified record if it exists"""
        res = get_message_template(id=id)

        return res.to_dict() if res else None

    def get_all_message_templates(self) -> AllMessageTemplateTypes:
        """Get all message templates by category"""
        return get_all_message_templates()

    def add_message_template(
        self, title: str, content: str, category: str | MessageTemplateCategory, by: str
    ) -> int:
        """Add a new message template and return the ID of the new record"""
        return add_message_template(
            title=title, content=content, category=category, author=by
        )

    def delete_message_template(self, id: int) -> bool:
        """Delete a specific message template"""
        return delete_message_template(id=id)

    def edit_message_template(
        self,
        id: int,
        title: str | None,
        content: str | None,
        category: str | MessageTemplateCategory | None,
        by: str,
    ) -> None:
        """Add a new message template and return the ID of the new record"""
        return edit_message_template(
            id=id, title=title, content=content, category=category, author=by
        )

    def get_webhook_queue_overview(
        self, queue_id: str
    ) -> webhook_service.QueueStatus | None:
        return webhook_service.get_queue_overview(queue_id=queue_id)

    def get_all_webhook_queues(self) -> list[str]:
        return webhook_service.get_all_queue_keys()

    def get_webhook_service_summary(self):
        """Return the overall status of the service

        All webhook queues, the number of queued messages, their rate limit bucket,
        the number of rate limits each bucket has had and whether we are globally rate limited
        """
        return webhook_service.webhook_service_summary()

    def reset_webhook_queues(self) -> int:
        """Delete each queue; unprocessed messages may be lost depending on timing"""
        return webhook_service.reset_webhook_queues()

    def reset_all_webhook_queues_for_server_number(
        self, server_number: int | str
    ) -> int:
        """Delete each queue associated with the specified server number"""
        return webhook_service.reset_all_queues_for_server_number(
            server_number=server_number
        )

    def reset_webhook_queue(self, queue_id: str) -> bool:
        """Delete the specified queue; returning if it deleted any entries"""
        return webhook_service.reset_queue(queue_id=queue_id)

    def reset_webhook_queue_type(
        self, webhook_type: webhook_service.WebhookType | str
    ) -> int:
        """Delete each queue of wh_type (discord, etc.) returning the number of deleted queues"""
        return webhook_service.reset_queue_type(webhook_type=webhook_type)

    def reset_webhook_message_type(
        self, message_type: webhook_service.WebhookMessageType | str
    ) -> int:
        """Delete each queue of wh_type (discord, etc.) returning the number of deleted queues"""
        return webhook_service.reset_message_type(message_type=message_type)

    def update_player_profile(
        self,
        player_id: str,
        email: str | MissingType = MISSING,
        discord_id: str | MissingType = MISSING,
    ):
        return update_player_profile(
            player_id=player_id, email=email, discord_id=discord_id
        )

    # VIP List Endpoints
    def get_vip_lists(
        self, with_records: bool = False
    ) -> list[VipListType | VipListTypeWithRecordsType]:
        with enter_session() as sess:
            return [
                lst.to_dict(with_records=with_records)
                for lst in vip.get_vip_lists(sess=sess)
            ]

    def get_vip_lists_for_server(self) -> list[VipListType]:
        with enter_session() as sess:
            return [
                lst.to_dict()
                for lst in vip.get_vip_lists_for_server(
                    sess=sess, server_number=SERVER_NUMBER
                )
            ]

    def get_vip_list(
        self, vip_list_id: int, strict: bool = False, with_records: bool = False
    ) -> VipListType | None:
        with enter_session() as sess:
            new_list = vip.get_vip_list(
                sess=sess, vip_list_id=vip_list_id, strict=strict
            )
            return new_list.to_dict(with_records=with_records) if new_list else None

    def create_vip_list(
        self, name: str, sync: VipListSyncMethod, servers: Sequence[int] | None
    ) -> VipListType:
        return vip.create_vip_list(name=name, sync=sync, servers=servers)

    def edit_vip_list(
        self,
        vip_list_id: int,
        name: str | MissingType = MISSING,
        sync: VipListSyncMethod | MissingType = MISSING,
        servers: Sequence[int] | MissingType = MISSING,
    ) -> VipListType | None:
        return vip.edit_vip_list(
            vip_list_id=vip_list_id, name=name, sync=sync, servers=servers
        )

    def delete_vip_list(self, vip_list_id: int) -> bool:
        return vip.delete_vip_list(vip_list_id=vip_list_id)

    def get_vip_record(
        self, record_id: int, strict: bool = False
    ) -> VipListRecordType | None:
        with enter_session() as sess:
            record = vip.get_vip_record(sess=sess, record_id=record_id, strict=strict)
            return record.to_dict() if record else None

    def add_vip_list_record(
        self,
        player_id: str,
        vip_list_id: int,
        description: str | None = None,
        active: bool = True,
        expires_at: datetime | None = None,
        notes: str | None = None,
        admin_name: str = "CRCON",
    ) -> VipListRecordType | None:
        return vip.add_record_to_vip_list(
            player_id=player_id,
            vip_list_id=vip_list_id,
            description=description,
            active=active,
            expires_at=expires_at,
            notes=notes,
            admin_name=admin_name,
        )

    def edit_vip_list_record(
        self,
        record_id: int,
        vip_list_id: int | MissingType = MISSING,
        description: str | MissingType = MISSING,
        active: bool | MissingType = MISSING,
        expires_at: datetime | MissingType = MISSING,
        notes: str | MissingType = MISSING,
        admin_name: str = "CRCON",
    ) -> VipListRecordType | None:
        return vip.edit_vip_list_record(
            record_id=record_id,
            vip_list_id=vip_list_id,
            description=description,
            active=active,
            expires_at=expires_at,
            notes=notes,
            admin_name=admin_name,
        )

    def add_or_edit_vip_list_record(
        self,
        player_id: str,
        vip_list_id: int,
        description: str | MissingType = MISSING,
        active: bool | MissingType = MISSING,
        expires_at: datetime | MissingType = MISSING,
        notes: str | MissingType = MISSING,
        admin_name: str = "CRCON",
    ):
        return vip.add_or_edit_vip_list_record(
            player_id=player_id,
            vip_list_id=vip_list_id,
            description=description,
            active=active,
            expires_at=expires_at,
            notes=notes,
            admin_name=admin_name,
        )

    def bulk_add_vip_list_records(
        self, records: Iterable[VipListRecordType]
    ) -> None | defaultdict[str, set[int]]:
        return vip.bulk_add_vip_records(records=records)

    def bulk_delete_vip_list_records(self, record_ids: Iterable[int]):
        return vip.bulk_delete_vip_records(record_ids=record_ids)

    def bulk_edit_vip_list_records(
        self, records: Iterable[VipListRecordEditType]
    ) -> None:
        return vip.bulk_edit_vip_records(records=records)

    def delete_vip_list_record(
        self,
        record_id: int,
    ) -> bool:
        return vip.delete_vip_list_record(record_id=record_id)

    def get_vip_status_for_player_ids(
        self, player_ids: set[str]
    ) -> dict[str, VipListRecordType]:
        return vip.get_vip_status_for_player_ids(player_ids=player_ids)

    def get_active_vip_records(self, vip_list_id: int) -> list[VipListRecordType]:
        with enter_session() as sess:
            return [
                record.to_dict()
                for record in vip.get_active_vip_records(
                    sess=sess, vip_list_id=vip_list_id
                )
            ]

    def get_inactive_vip_records(self, vip_list_id: int) -> list[VipListRecordType]:
        with enter_session() as sess:
            return [
                record.to_dict()
                for record in vip.get_inactive_vip_records(
                    sess=sess, vip_list_id=vip_list_id
                )
            ]

    def get_player_vip_records(
        self,
        player_id: str,
        include_expired: bool = True,
        include_inactive: bool = True,
        include_other_servers=True,
        exclude: set[int] | None = None,
    ) -> list[VipListRecordType]:
        with enter_session() as sess:
            return [
                record.to_dict()
                for record in vip.get_player_vip_list_records(
                    sess=sess,
                    player_id=player_id,
                    include_expired=include_expired,
                    include_inactive=include_inactive,
                    include_other_servers=include_other_servers,
                    exclude=exclude,
                )
            ]

    def get_vip_list_records(
        self,
        player_id: str | None = None,
        # Can't use admin_name without the API introspection will set it
        # whatever user made the API call
        author_admin_name: str | None = None,
        active: bool | None = None,
        description_or_player_name: str | None = None,
        notes: str | None = None,
        vip_list_id: int | None = None,
        exclude_expired: bool = False,
        page_size: int = 50,
        page: int = 1,
    ):
        # TODO: type this
        with enter_session() as sess:
            records, total_records = vip.search_vip_list_records(
                sess=sess,
                player_id=player_id,
                admin_name=author_admin_name,
                active=active,
                description_or_player_name=description_or_player_name,
                notes=notes,
                vip_list_id=vip_list_id,
                exclude_expired=exclude_expired,
                page_size=page_size,
                page=page,
            )

            return {
                "records": [record.to_dict(with_vip_list=True) for record in records],
                "total": total_records,
            }

    def get_all_vip_records_for_server(
        self, server_number: int
    ) -> list[VipListRecordType]:
        with enter_session() as sess:
            return [
                record.to_dict()
                for record in vip.get_all_records_for_server(
                    sess=sess, server_number=server_number
                )
            ]

    def inactivate_expired_vip_records(self) -> None:
        return vip.inactivate_expired_records()

    def extend_vip_duration(
        self, player_id: str, vip_list_id: int, duration: timedelta | int
    ) -> VipListRecordType | None:
        return vip.extend_vip_duration(
            player_id=player_id, vip_list_id=vip_list_id, duration=duration
        )

    def revoke_all_vip(self, player_id: str):
        return vip.revoke_all_vip(player_id=player_id)

    def synchronize_with_game_server(self):
        return vip.synchronize_with_game_server(server_number=SERVER_NUMBER)

    def convert_old_style_vip_records(self, records: Iterable[str], vip_list_id: int):
        return vip.convert_old_style_vip_records(
            records=records, vip_list_id=vip_list_id
        )

    # End VIP List Endpoints
