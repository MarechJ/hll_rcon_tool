import inspect
from datetime import datetime
from logging import getLogger
from typing import Any, Iterable, Literal, Optional, Type

from dateutil import parser

from rcon import game_logs, player_history
from rcon.audit import ingame_mods, online_mods
from rcon.cache_utils import RedisCached, get_redis_pool
from rcon.discord import audit_user_config_differences
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
from rcon.user_config.utils import BaseUserConfig, validate_user_config
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

    @staticmethod
    def _validate_user_config(
        command_name: str,
        by: str,
        model: Type[BaseUserConfig],
        data: dict[str, Any] | BaseUserConfig,
        dry_run: bool = True,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
    ):
        old_model = model.load_from_db()
        res = validate_user_config(
            model=model,
            data=data,
            dry_run=dry_run,
            errors_as_json=errors_as_json,
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

    def blacklist_player(
        self,
        player_id: str,
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
            player_id: steam_id_64 or windows store ID
            reason: The reason the player was blacklisted
            player_name: The players name which will be added as an alias
            audit_name: The person/tool that is blacklisting the player
        """

        # Attempt to perma ban on the server for immediate removal
        try:
            self.perma_ban(
                player_name=player_name,
                player_id=player_id,
                reason=reason,
                by=audit_name if audit_name else "",
            )
        except Exception as e:
            logger.exception(e)
            logger.error(
                "%s while attempting to perma ban in blacklist_player %s, %s",
                e,
                player_id,
                player_name,
            )

        # This is redundant since the player is added to the blacklist in `perma_ban`
        # but including it here to preserve functionality with the blacklist regardless of
        # whether or not the player is perma banned or blacklisted
        # legacy game server versions would not let you perma ban a player who was not connected
        add_player_to_blacklist(
            steam_id_64=player_id, reason=reason, name=player_name, by=audit_name
        )

        return True

    def unban(
        self,
        player_id: str,
    ) -> bool:
        """Remove all temporary and permanent bans from the player_id

        Args:
            player_id: steam_id_64 or windows store ID
        """
        bans = self.get_bans()
        type_to_func = {
            "temp": self.remove_temp_ban,
            "perma": self.remove_perma_ban,
        }
        for b in bans:
            if b.get("steam_id_64") == player_id:
                type_to_func[b["type"]](b["raw"])

        # unban broadcasting is handled in `rconweb.api.views.expose_api_endpoints`
        config = RconServerSettingsUserConfig.load_from_db()
        if config.unban_does_unblacklist:
            remove_player_from_blacklist(steam_id_64=player_id)

        return True

    def unblacklist_player(
        self,
        player_id: str,
    ) -> bool:
        """
        Remove a player from the blacklist

        The blacklist is a permanent ban list stored in CRCON so it persists
        between game servers if you move providers or your files are reset and
        each player is automatically checked when they connect and permanently
        banned if they are on the list.

        Args:
            player_id: steam_id_64 or windows store ID
        """

        remove_player_from_blacklist(steam_id_64=player_id)

        return True

    def clear_cache(self) -> bool:
        """Clear every key in this servers Redis cache

        Many things in CRCON are cached in Redis to avoid excessively polling
        the game server, this clears the entire cache which is sometimes necessary
        to force a refresh
        """
        # TODO: allow clearing specific cache keys
        return RedisCached.clear_all_caches(get_redis_pool())

    def get_player_profile(
        self,
        player_id: str | None = None,
        player_db_id: int | None = None,
        num_sessions: int = 10,
    ) -> PlayerProfileType | None:
        if player_id:
            return player_history.get_player_profile(
                player_id=player_id, nb_sessions=num_sessions
            )
        else:
            return player_history.get_player_profile_by_id(
                id=player_db_id, nb_sessions=num_sessions
            )

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
        # TODO: this isn't used, can we remove it?
        type_map = {
            "last_seen_from": parser.parse,
            "last_seen_till": parser.parse,
            "player_name": str,
            "blacklisted": bool,
            "is_watched": bool,
            "player_id": str,
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
            steam_id_64=player_id,
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
            steam_id_64=player_id, flag=flag, comment=comment, player_name=player_name
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
            flag_id=flag_id, steam_id_64=player_id, flag=flag
        )
        return removed_flag

    def set_server_name(self, name: str):
        # TODO: server name won't change until map change
        # but the cache also needs to be cleared, but can't
        # immediately clear or it will just refresh but we
        # can use a timer

        gtx = GTXFtp.from_config()
        gtx.change_server_name(new_name=name)

    @staticmethod
    def toggle_player_watch(
        player_id: str,
        audit_name: str,
        add: bool,
        reason: str | None = None,
        player_name: str | None = None,
    ) -> bool:
        watcher = PlayerWatch(steam_id_64=player_id)
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
        by: str,
        reason: str | None = None,
        player_name: str | None = None,
    ) -> bool:
        return self.toggle_player_watch(
            player_id=player_id,
            player_name=player_name,
            reason=reason,
            audit_name=by,
            add=False,
        )

    def get_online_mods(self) -> list[str]:
        return online_mods()

    def get_ingame_mods(self) -> list[AdminUserType]:
        return ingame_mods()

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
        output: str | None = None,
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
        # TODO: update this when we return `Layer`s instead of strings
        return {
            "votes": {k: str(v) for k, v in v.get_votes().items()},
            "selection": [str(m) for m in v.get_selection()],
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

        # TODO: update this when we return `Layer`s instead of strings
        return [str(map) for map in v.get_map_whitelist()]

    def add_map_to_whitelist(self, map_name: str):
        v = VoteMap()
        v.add_map_to_whitelist(map_name=map_name)

    def add_maps_to_vm_whitelist(self, map_names: Iterable[str]):
        v = VoteMap()
        v.add_maps_to_vm_whitelist(map_names=map_names)

    def remove_map_from_vm_whitelist(self, map_name: str):
        v = VoteMap()
        v.remove_map_from_vm_whitelist(map_name=map_name)

    def remove_maps_from_vm_whitelist(self, map_names: Iterable[str]):
        v = VoteMap()
        v.remove_maps_from_vm_whitelist(map_names=map_names)

    def reset_map_vm_whitelist(self):
        v = VoteMap()
        v.reset_map_vm_whitelist()

    def set_map_vm_whitelist(self, map_names: Iterable[str]):
        v = VoteMap()
        v.set_map_vm_whitelist(map_names=map_names)

    def get_votemap_config(self) -> VoteMapUserConfig:
        return VoteMapUserConfig.load_from_db()

    def validate_votemap_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            by=by,
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            model=VoteMapUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def set_votemap_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            by=by,
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
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
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=AutoBroadcastUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def set_auto_broadcasts_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
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
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=AutoVoteKickUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def set_votekick_autotoggle_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
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
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=AutoModLevelUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def set_auto_mod_level_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
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
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=AutoModNoLeaderUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def set_auto_mod_no_leader_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
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
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=AutoModSeedingUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def set_auto_mod_seeding_config(
        self,
        by: str,
        user_config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
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
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=AutoModNoSoloTankUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def set_auto_mod_solo_tank_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
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
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=BanTeamKillOnConnectUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def set_tk_ban_on_connect_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
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
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=RealVipUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def set_real_vip_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
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
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=CameraNotificationUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_camera_notification_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
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
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=ExpiredVipsUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_expired_vip_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
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
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=GtxServerNameChangeUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_server_name_change_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
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
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=LogLineWebhookUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_log_line_webhook_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
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
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=NameKickUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_name_kick_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
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
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=RconConnectionSettingsUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_rcon_connection_settings_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
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
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=RconServerSettingsUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_rcon_server_settings_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
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
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=ScorebotUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_scorebot_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
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
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=StandardBroadcastMessagesUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_standard_broadcast_messages(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
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
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=StandardPunishmentMessagesUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_standard_punishments_messages(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
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
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=StandardWelcomeMessagesUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_standard_welcome_messages(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
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
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=SteamUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_steam_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
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
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=VacGameBansUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_vac_game_bans_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
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
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=AdminPingWebhooksUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_admin_pings_discord_webhooks_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
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
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=AuditWebhooksUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_audit_discord_webhooks_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=AuditWebhooksUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_camera_discord_webhooks_config(self) -> CameraWebhooksUserConfig:
        return CameraWebhooksUserConfig.load_from_db()

    def set_camera_discord_webhooks_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=CameraWebhooksUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_camera_discord_webhooks_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
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
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=ChatWebhooksUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_chat_discord_webhooks_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
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
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            by=by,
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            model=KillsWebhooksUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_kills_discord_webhooks_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
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
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=WatchlistWebhooksUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_watchlist_discord_webhooks_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
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
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=ChatCommandsUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_chat_commands_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=ChatCommandsUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def get_log_stream_config(self):
        return LogStreamUserConfig.load_from_db()

    def set_log_stream_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=LogStreamUserConfig,
            data=config or kwargs,
            dry_run=False,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )

    def validate_log_stream_config(
        self,
        by: str,
        config: dict[str, Any] | BaseUserConfig | None = None,
        errors_as_json: bool = False,
        reset_to_default: bool = False,
        **kwargs,
    ) -> bool:
        return self._validate_user_config(
            command_name=inspect.currentframe().f_code.co_name,  # type: ignore
            by=by,
            model=LogStreamUserConfig,
            data=config or kwargs,
            dry_run=True,
            errors_as_json=errors_as_json,
            reset_to_default=reset_to_default,
        )