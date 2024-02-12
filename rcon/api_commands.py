from datetime import datetime
from logging import getLogger
from typing import Any, Iterable, Literal, Optional, Type

import pydantic
from dateutil import parser

from rcon import game_logs, player_history
from rcon.audit import ingame_mods, online_mods
from rcon.cache_utils import RedisCached, get_redis_pool
from rcon.gtx import GTXFtp
from rcon.player_history import (
    add_flag_to_player,
    add_player_to_blacklist,
    get_players_by_appearance,
    remove_flag,
    remove_player_from_blacklist,
)
from rcon.rcon import Rcon
from rcon.server_stats import get_db_server_stats_for_range
from rcon.settings import SERVER_INFO
from rcon.types import (
    AdminUserType,
    ParsedLogsType,
    PlayerFlagType,
    PlayerProfileType,
    ServerInfoType,
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
from rcon.user_config.expired_vips import ExpiredVipsUserConfig
from rcon.user_config.gtx_server_name import GtxServerNameChangeUserConfig
from rcon.user_config.log_line_webhooks import LogLineWebhookUserConfig
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
from rcon.user_config.utils import BaseUserConfig, set_user_config
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
from rcon.vote_map import VoteMap
from rcon.watchlist import PlayerWatch

logger = getLogger(__name__)

CTL: Optional["RconAPI"] = None


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

    def do_blacklist_player(
        self,
        steam_id_64: str,
        reason: str,
        player_name: str | None = None,
        audit_name: str | None = None,
    ) -> bool:
        """
        Add a player to the blacklist

        The blacklist is a permanent ban list stored in CRCON so it persists
        between game servers if you move providers or your files are reset and
        each player is automatically checked when they connect and permanently
        banned if they are on the list.

        Args:
            steam_id_64: steam_id_64 or windows store ID
            reason: The reason the player was blacklisted
            player_name: The players name which will be added as an alias
            audit_name: The person/tool that is blacklisting the player
        """

        # Attempt to perma ban on the server for immediate removal
        try:
            self.do_perma_ban(
                player=player_name,
                steam_id_64=steam_id_64,
                reason=reason,
                by=audit_name if audit_name else "",
            )
        except Exception as e:
            logger.exception(e)
            logger.error(
                "%s while attempting to perma ban in do_blacklist_player %s, %s",
                e,
                steam_id_64,
                player_name,
            )

        # This is redundant since the player is added to the blacklist in `do_perma_ban`
        # but including it here to preserve functionality with the blacklist regardless of
        # whether or not the player is perma banned or blacklisted
        # legacy game server versions would not let you perma ban a player who was not connected
        add_player_to_blacklist(
            steam_id_64=steam_id_64, reason=reason, name=player_name, by=audit_name
        )

        return True

    def blacklist_player(
        self,
        steam_id_64: str,
        reason: str,
        player_name: str | None = None,
        audit_name: str | None = None,
    ):
        """This is DEPRECATED use do_blacklist_player instead, it will be removed in a future release"""
        # TODO: remove this deprecated endpoint
        return self.do_blacklist_player(
            steam_id_64=steam_id_64,
            reason=reason,
            player_name=player_name,
            audit_name=audit_name,
        )

    def do_unban(
        self,
        steam_id_64: str,
    ) -> bool:
        """Remove all temporary and permanent bans from the steam_id_64

        Args:
            steam_id_64: steam_id_64 or windows store ID
        """
        # logger.info(f"do_unban {steam_id_64=} {kwargs=}")
        bans = self.get_bans()
        type_to_func = {
            "temp": self.do_remove_temp_ban,
            "perma": self.do_remove_perma_ban,
        }
        for b in bans:
            if b.get("steam_id_64") == steam_id_64:
                type_to_func[b["type"]](b["raw"])

        # unban broadcasting is handled in `rconweb.api.views.expose_api_endpoints`
        config = RconServerSettingsUserConfig.load_from_db()
        if config.unban_does_unblacklist:
            remove_player_from_blacklist(steam_id_64=steam_id_64)

        return True

    def unban(
        self,
        steam_id_64: str,
    ) -> bool:
        """This is DEPRECATED use do_unban instead, it will be removed in a future release"""
        # TODO: remove this deprecated endpoint
        return self.do_unban(
            steam_id_64=steam_id_64,
        )

    def do_unblacklist_player(
        self,
        steam_id_64: str,
    ) -> bool:
        """
        Remove a player from the blacklist

        The blacklist is a permanent ban list stored in CRCON so it persists
        between game servers if you move providers or your files are reset and
        each player is automatically checked when they connect and permanently
        banned if they are on the list.

        Args:
            steam_id_64: steam_id_64 or windows store ID
        """

        remove_player_from_blacklist(steam_id_64=steam_id_64)

        return True

    def unblacklist_player(
        self,
        steam_id_64: str,
    ):
        return self.do_unblacklist_player(steam_id_64=steam_id_64)

    def do_clear_cache(self) -> bool:
        """Clear every key in this servers Redis cache

        Many things in CRCON are cached in Redis to avoid excessively polling
        the game server, this clears the entire cache which is sometimes necessary
        to force a refresh
        """
        # TODO: allow clearing specific cache keys
        return RedisCached.clear_all_caches(get_redis_pool())

    def clear_cache(self):
        return self.do_clear_cache()

    def get_player_profile(
        self,
        steam_id_64: str | None = None,
        player_db_id: int | None = None,
        num_sessions: int = 10,
    ) -> PlayerProfileType | None:
        if steam_id_64:
            return player_history.get_player_profile(
                steam_id_64=steam_id_64, nb_sessions=num_sessions
            )
        else:
            return player_history.get_player_profile_by_id(
                id=player_db_id, nb_sessions=num_sessions
            )

    def player(
        self,
        steam_id_64: str | None = None,
        player_db_id: int | None = None,
        num_sessions: int = 10,
    ):
        """This is DEPRECATED use get_player_profile instead, it will be removed in a future release"""
        # TODO: remove this deprecated endpoint
        return self.get_player_profile(
            steam_id_64=steam_id_64,
            player_db_id=player_db_id,
            num_sessions=num_sessions,
        )

    def get_players_history(
        self,
        page: int = 1,
        page_size: int = 500,
        last_seen_from: datetime | None = None,
        last_seen_till: datetime | None = None,
        steam_id_64: str | None = None,
        player_name: str | None = None,
        blacklisted: bool | None = None,
        is_watched: bool | None = None,
        exact_name_match: bool = False,
        ignore_accent: bool = True,
        flags: str | list[str] | None = None,
        country: str | None = None,
    ):
        type_map = {
            "last_seen_from": parser.parse,
            "last_seen_till": parser.parse,
            "player_name": str,
            "blacklisted": bool,
            "is_watched": bool,
            "steam_id_64": str,
            "page": int,
            "page_size": int,
            "ignore_accent": bool,
            "exact_name_match": bool,
            "country": str,
            "flags": lambda s: [f for f in s.split(",") if f] if s else "",
        }

        return get_players_by_appearance(
            page=page,
            page_size=page_size,
            last_seen_from=last_seen_from,
            last_seen_till=last_seen_till,
            player_name=player_name,
            blacklisted=blacklisted,
            steam_id_64=steam_id_64,
            is_watched=is_watched,
            exact_name_match=exact_name_match,
            ignore_accent=ignore_accent,
            flags=flags,
            country=country,
        )

    def players_history(
        self,
        page: int = 1,
        page_size: int = 500,
        last_seen_from: datetime | None = None,
        last_seen_till: datetime | None = None,
        steam_id_64: str | None = None,
        player_name: str | None = None,
        blacklisted: bool | None = None,
        is_watched: bool | None = None,
        exact_name_match: bool = False,
        ignore_accent: bool = True,
        flags: str | list[str] | None = None,
        country: str | None = None,
    ):
        """This is DEPRECATED use get_players_history instead, it will be removed in a future release"""
        # TODO: remove this deprecated endpoint
        return self.get_players_history(
            page=page,
            page_size=page_size,
            last_seen_from=last_seen_from,
            last_seen_till=last_seen_till,
            steam_id_64=steam_id_64,
            player_name=player_name,
            blacklisted=blacklisted,
            is_watched=is_watched,
            exact_name_match=exact_name_match,
            ignore_accent=ignore_accent,
            flags=flags,
            country=country,
        )

    def do_flag_player(
        self,
        steam_id_64: str,
        flag: str,
        player_name: str | None = None,
        comment: str | None = None,
    ) -> PlayerFlagType:
        """Adds a new flag to the specified steam_id_64

        Flags are used to label users and some tools use the flags to whitelist
        users. They are traditionally an emoji (the frontend uses an emoji picker)
        but there is no length restriction in the database.

        Args:
            steam_id_64: steam_id_64 or windows store ID
            player_name: The players name which will be added as an alias
            flag:
            comment:


        """

        player, new_flag = add_flag_to_player(
            steam_id_64=steam_id_64, flag=flag, comment=comment, player_name=player_name
        )
        # TODO: can we preserve discord auditing with player aliases?
        # data["player_name"] = " | ".join(n["name"] for n in player["names"])

        return new_flag

    def flag_player(
        self,
        steam_id_64: str,
        flag: str,
        player_name: str | None = None,
        comment: str | None = None,
    ):
        """This is DEPRECATED use do_flag_player instead, it will be removed in a future release"""
        # TODO: remove this deprecated endpoint
        return self.do_flag_player(
            steam_id_64=steam_id_64, player_name=player_name, flag=flag, comment=comment
        )

    def do_unflag_player(
        self,
        flag_id: int | None = None,
        steam_id_64: str | None = None,
        flag: str | None = None,
    ) -> PlayerFlagType:
        """Flags can be removed either by flag_id (database key) or by passing a player ID and flag

        Args:
            flag_id: The database primary key of the flag record to delete
            steam_id_64: steam_id_64 or windows store ID
            flag: The flag to remove from `steam_id_64` if present
        """
        player, removed_flag = remove_flag(
            flag_id=flag_id, steam_id_64=steam_id_64, flag=flag
        )
        return removed_flag

    def unflag_player(self, flag_id: int):
        """This is DEPRECATED use do_unflag_player instead, it will be removed in a future release"""
        # TODO: remove this deprecated endpoint
        return self.do_unflag_player(flag_id=flag_id)

    def set_server_name(self, name: str):
        # TODO: server name won't change until map change
        # but the cache also needs to be cleared, but can't
        # immediately clear or it will just refresh but we
        # can use a timer

        gtx = GTXFtp.from_config()
        gtx.change_server_name(new_name=name)

    @staticmethod
    def toggle_player_watch(
        steam_id_64: str,
        audit_name: str,
        add: bool,
        reason: str | None = None,
        player_name: str | None = None,
    ) -> bool:
        watcher = PlayerWatch(steam_id_64=steam_id_64)
        if add:
            result = watcher.watch(
                reason=reason or "",
                by=audit_name,
                player_name=player_name or "",
            )
        else:
            result = watcher.unwatch()

        return result

    def do_watch_player(
        self,
        steam_id_64: str,
        reason: str,
        by: str,
        player_name: str | None = None,
    ) -> bool:
        return self.toggle_player_watch(
            steam_id_64=steam_id_64,
            player_name=player_name,
            reason=reason,
            audit_name=by,
            add=True,
        )

    def do_unwatch_player(
        self,
        steam_id_64: str,
        by: str,
        reason: str | None = None,
        player_name: str | None = None,
    ) -> bool:
        return self.toggle_player_watch(
            steam_id_64=steam_id_64,
            player_name=player_name,
            reason=reason,
            audit_name=by,
            add=False,
        )

    def run_raw_command(self):
        # TODO: how to handle both get/post methods
        pass

    def get_online_mods(self) -> list[str]:
        return online_mods()

    def get_ingame_mods(self) -> list[AdminUserType]:
        return ingame_mods()

    def get_historical_logs(
        self,
        player_name: str | None = None,
        steam_id_64: str | None = None,
        action: str | None = None,
        limit: int = 1000,
        from_: datetime | None = None,
        till: datetime | None = None,
        time_sort: Literal["desc", "asc"] = "desc",
        exact_player_match: bool = False,
        exact_action: bool = True,
        output: str | None = None,
    ):
        lines = game_logs.get_historical_logs(
            player_name=player_name,
            action=action,
            steam_id_64=steam_id_64,
            limit=limit,
            from_=from_,
            till=till,
            time_sort=time_sort,
            exact_player_match=exact_player_match,
            exact_action=exact_action,
        )

        if output and output.upper() == "CSV":
            # TODO: csv output
            pass
        else:
            return lines

    def get_recent_logs(
        self,
        filter_player: list[str] = [],
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

    def get_server_stats(
        self,
        by_map,
        with_players,
        start: datetime | None = None,
        end: datetime | None = None,
    ):
        return get_db_server_stats_for_range(
            start=start, end=end, by_map=by_map, with_player_list=with_players
        )

    def get_votemap_status(self) -> VoteMapStatusType:
        v = VoteMap()

        # TODO: finish this typing
        return {
            "votes": v.get_votes(),
            "selection": v.get_selection(),
            "results": v.get_vote_overview(),
        }

    def reset_votemap_state(self) -> VoteMapStatusType:
        v = VoteMap()
        v.clear_votes()
        v.gen_selection()
        v.apply_results()

        return self.get_votemap_status()

    def get_map_whitelist(self) -> list[str]:
        v = VoteMap()

        return [map for map in v.get_map_whitelist()]

    def do_add_map_to_whitelist(self, map_name: str):
        v = VoteMap()
        v.do_add_map_to_whitelist(map_name=map_name)

    def do_add_maps_to_whitelist(self, map_names: Iterable[str]):
        v = VoteMap()
        v.do_add_maps_to_whitelist(map_names=map_names)

    def do_remove_map_from_whitelist(self, map_name: str):
        v = VoteMap()
        v.do_remove_map_from_whitelist(map_name=map_name)

    def do_remove_maps_from_whitelist(self, map_names: Iterable[str]):
        v = VoteMap()
        v.do_remove_maps_from_whitelist(map_names=map_names)

    def do_reset_map_whitelist(self):
        v = VoteMap()
        v.do_reset_map_whitelist()

    def do_set_map_whitelist(self, map_names: Iterable[str]):
        v = VoteMap()
        v.do_set_map_whitelist(map_names=map_names)

    @staticmethod
    def _validate_user_config(
        model: Type[BaseUserConfig],
        data: dict[str, Any] | BaseUserConfig,
        dry_run: bool = True,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
    ) -> bool:
        if isinstance(data, BaseUserConfig):
            dumped_model = data.model_dump()
        else:
            dumped_model = data

        if reset_to_default:
            try:
                default = model()
                result = default.model_dump()
                set_user_config(default.KEY(), result)
                return True
            except pydantic.ValidationError as e:
                if errors_as_json:
                    error_msg = e.json()
                else:
                    error_msg = str(e)
                logger.warning(error_msg)
                return False

        try:
            model.save_to_db(values=dumped_model, dry_run=dry_run)
        except pydantic.ValidationError as e:
            if errors_as_json:
                error_msg = e.json()
            else:
                error_msg = str(e)
            logger.warning(error_msg)
            return False

        return True

    def get_votemap_config(self) -> VoteMapUserConfig:
        return VoteMapUserConfig.load_from_db()

    def validate_votemap_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=VoteMapUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def set_votemap_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=VoteMapUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_auto_broadcasts_config(self) -> AutoBroadcastUserConfig:
        return AutoBroadcastUserConfig.load_from_db()

    def validate_auto_broadcasts_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=AutoBroadcastUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def set_auto_broadcasts_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=AutoBroadcastUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_votekick_autotoggle_config(self) -> AutoVoteKickUserConfig:
        return AutoVoteKickUserConfig.load_from_db()

    def validate_votekick_autotoggle_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=AutoVoteKickUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def set_votekick_autotoggle_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=AutoVoteKickUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_auto_mod_level_config(self) -> AutoModLevelUserConfig:
        return AutoModLevelUserConfig.load_from_db()

    def validate_auto_mod_level_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=AutoModLevelUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def set_auto_mod_level_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=AutoModLevelUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_auto_mod_no_leader_config(self) -> AutoModNoLeaderUserConfig:
        return AutoModNoLeaderUserConfig.load_from_db()

    def validate_auto_mod_no_leader_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=AutoModNoLeaderUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def set_auto_mod_no_leader_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=AutoModNoLeaderUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_auto_mod_seeding_config(self) -> AutoModSeedingUserConfig:
        return AutoModSeedingUserConfig.load_from_db()

    def validate_auto_mod_seeding_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=AutoModSeedingUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def set_auto_mod_seeding_config(
        self,
        user_config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=AutoModSeedingUserConfig,
            data=user_config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_auto_mod_solo_tank_config(self) -> AutoModNoSoloTankUserConfig:
        return AutoModNoSoloTankUserConfig.load_from_db()

    def validate_auto_mod_solo_tank_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=AutoModNoSoloTankUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def set_auto_mod_solo_tank_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=AutoModNoSoloTankUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_tk_ban_on_connect_config(self) -> BanTeamKillOnConnectUserConfig:
        return BanTeamKillOnConnectUserConfig.load_from_db()

    def validate_tk_ban_on_connect_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=BanTeamKillOnConnectUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def set_tk_ban_on_connect_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=BanTeamKillOnConnectUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_real_vip_config(
        self,
    ) -> RealVipUserConfig:
        return RealVipUserConfig.load_from_db()

    def validate_real_vip_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=RealVipUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def set_real_vip_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=RealVipUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_camera_notification_config(self) -> CameraNotificationUserConfig:
        return CameraNotificationUserConfig.load_from_db()

    def set_camera_notification_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=CameraNotificationUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_camera_notification_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=CameraNotificationUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_expired_vip_config(self) -> ExpiredVipsUserConfig:
        return ExpiredVipsUserConfig.load_from_db()

    def set_expired_vip_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=ExpiredVipsUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_expired_vip_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=ExpiredVipsUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_server_name_change_config(self) -> GtxServerNameChangeUserConfig:
        return GtxServerNameChangeUserConfig.load_from_db()

    def set_server_name_change_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=GtxServerNameChangeUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_server_name_change_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=GtxServerNameChangeUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_log_line_webhook_config(self) -> LogLineWebhookUserConfig:
        return LogLineWebhookUserConfig.load_from_db()

    def set_log_line_webhook_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=LogLineWebhookUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_log_line_webhook_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=LogLineWebhookUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_name_kick_config(self) -> NameKickUserConfig:
        return NameKickUserConfig.load_from_db()

    def set_name_kick_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=NameKickUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_name_kick_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=NameKickUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_rcon_connection_settings_config(self) -> RconConnectionSettingsUserConfig:
        return RconConnectionSettingsUserConfig.load_from_db()

    def set_rcon_connection_settings_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=RconConnectionSettingsUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_rcon_connection_settings_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=RconConnectionSettingsUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_rcon_server_settings_config(self) -> RconServerSettingsUserConfig:
        return RconServerSettingsUserConfig.load_from_db()

    def set_rcon_server_settings_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=RconServerSettingsUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_rcon_server_settings_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=RconServerSettingsUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_scorebot_config(self) -> ScorebotUserConfig:
        return ScorebotUserConfig.load_from_db()

    def set_scorebot_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=ScorebotUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_scorebot_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=ScorebotUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_standard_broadcast_messages(self) -> StandardBroadcastMessagesUserConfig:
        return StandardBroadcastMessagesUserConfig.load_from_db()

    def set_standard_broadcast_messages(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=StandardBroadcastMessagesUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_standard_broadcast_messages(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=StandardBroadcastMessagesUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_standard_punishments_messages(self) -> StandardPunishmentMessagesUserConfig:
        return StandardPunishmentMessagesUserConfig.load_from_db()

    def set_standard_punishments_messages(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=StandardPunishmentMessagesUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_standard_punishments_messages(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=StandardPunishmentMessagesUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_standard_welcome_messages(self) -> StandardWelcomeMessagesUserConfig:
        return StandardWelcomeMessagesUserConfig.load_from_db()

    def set_standard_welcome_messages(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=StandardWelcomeMessagesUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_standard_welcome_messages(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=StandardWelcomeMessagesUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_steam_config(self) -> SteamUserConfig:
        return SteamUserConfig.load_from_db()

    def set_steam_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=SteamUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_steam_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=SteamUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_vac_game_bans_config(self) -> VacGameBansUserConfig:
        return VacGameBansUserConfig.load_from_db()

    def set_vac_game_bans_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=VacGameBansUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_vac_game_bans_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=VacGameBansUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_admin_pings_discord_webhooks_config(self) -> AdminPingWebhooksUserConfig:
        return AdminPingWebhooksUserConfig.load_from_db()

    def set_admin_pings_discord_webhooks_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=AdminPingWebhooksUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_admin_pings_discord_webhooks_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=AdminPingWebhooksUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_audit_discord_webhooks_config(self) -> AuditWebhooksUserConfig:
        return AuditWebhooksUserConfig.load_from_db()

    def set_audit_discord_webhooks_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=AuditWebhooksUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_audit_discord_webhooks_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=AdminPingWebhooksUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_camera_discord_webhooks_config(self) -> CameraWebhooksUserConfig:
        return CameraWebhooksUserConfig.load_from_db()

    def set_camera_discord_webhooks_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=CameraWebhooksUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_camera_discord_webhooks_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=CameraWebhooksUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_chat_discord_webhooks_config(self) -> ChatWebhooksUserConfig:
        return ChatWebhooksUserConfig.load_from_db()

    def set_chat_discord_webhooks_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=ChatWebhooksUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_chat_discord_webhooks_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=ChatWebhooksUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_kills_discord_webhooks_config(self):
        return KillsWebhooksUserConfig.load_from_db()

    def set_kills_discord_webhooks_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=KillsWebhooksUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_kills_discord_webhooks_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=KillsWebhooksUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_watchlist_discord_webhooks_config(self) -> WatchlistWebhooksUserConfig:
        return WatchlistWebhooksUserConfig.load_from_db()

    def set_watchlist_discord_webhooks_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=WatchlistWebhooksUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_watchlist_discord_webhooks_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=WatchlistWebhooksUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_chat_commands_config(self):
        return ChatCommandsUserConfig.load_from_db()

    def set_chat_commands_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=ChatCommandsUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_chat_commands_config(
        self,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            model=ChatCommandsUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )
