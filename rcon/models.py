import logging
import os
import re
from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Generator, List, Literal, Optional, Sequence, overload

import pydantic
from sqlalchemy import TIMESTAMP, Enum, ForeignKey, String, create_engine, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import InvalidRequestError, ProgrammingError
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    object_session,
    relationship,
    sessionmaker,
)
from sqlalchemy.schema import UniqueConstraint

from rcon.types import (
    AuditLogType,
    BlacklistRecordType,
    BlacklistRecordWithBlacklistType,
    BlacklistRecordWithPlayerType,
    BlacklistSyncMethod,
    BlacklistType,
    BlacklistWithRecordsType,
    DBLogLineType,
    MapsType,
    PenaltyCountType,
    PlayerActionState,
    PlayerActionType,
    PlayerAtCountType,
    PlayerCommentType,
    PlayerFlagType,
    PlayerNameType,
    PlayerOptinsType,
    PlayerProfileType,
    PlayerSessionType,
    PlayerStatsType,
    PlayerVIPType,
    ServerCountType,
    SteamBansType,
    SteamInfoType,
    SteamPlayerSummaryType,
    StructuredLogLineWithMetaData,
    WatchListType,
)
from rcon.utils import (
    SafeStringFormat,
    humanize_timedelta,
    mask_to_server_numbers,
    server_numbers_to_mask,
)

logger = logging.getLogger(__name__)

PLAYER_ID = "player_id"

_ENGINE = None


def get_engine():
    global _ENGINE

    if _ENGINE:
        return _ENGINE
    url = os.getenv("HLL_DB_URL")
    if not url:
        msg = "No $HLL_DB_URL specified. Can't use database features"
        logger.error(msg)
        raise ValueError(msg)

    _ENGINE = create_engine(url, echo=False)
    return _ENGINE


class Base(DeclarativeBase):
    # TODO: Replace dict[str, Any] w/ actual types
    type_annotation_map = {
        dict[str, Any]: JSONB,
        dict[str, int]: JSONB,
        SteamPlayerSummaryType: JSONB,
        SteamBansType: JSONB,
    }


class PlayerID(Base):
    __tablename__ = "steam_id_64"
    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[str] = mapped_column(
        "steam_id_64", nullable=False, index=True, unique=True
    )
    created: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    names: Mapped[list["PlayerName"]] = relationship(
        back_populates="player",
        order_by="nullslast(desc(PlayerName.last_seen))",
    )
    # If you ever change the ordering of sessions make sure you change the playtime calc code
    sessions: Mapped[list["PlayerSession"]] = relationship(
        back_populates="player",
        order_by="desc(PlayerSession.created)",
    )
    received_actions: Mapped[list["PlayersAction"]] = relationship(
        back_populates="player",
        order_by="desc(PlayersAction.time)",
    )
    flags: Mapped[list["PlayerFlag"]] = relationship(back_populates="player")
    watchlist: Mapped["WatchList"] = relationship(back_populates="player")
    steaminfo: Mapped["SteamInfo"] = relationship(back_populates="player")
    comments: Mapped[list["PlayerComment"]] = relationship(back_populates="player")
    stats: Mapped["PlayerStats"] = relationship(back_populates="player")
    blacklists: Mapped[list["BlacklistRecord"]] = relationship(back_populates="player")

    vips: Mapped[list["PlayerVIP"]] = relationship(
        back_populates="player",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    optins: Mapped[list["PlayerOptins"]] = relationship(back_populates="player")

    @property
    def server_number(self) -> int:
        return int(os.getenv("SERVER_NUMBER"))  # type: ignore

    @hybrid_property
    def vip(self) -> Optional["PlayerVIP"]:
        return (
            object_session(self)
            .query(PlayerVIP)  # type: ignore
            .filter(
                PlayerVIP.player_id_id == self.id,
                PlayerVIP.server_number == self.server_number,
            )
            .one_or_none()
        )

    def get_penalty_count(self) -> PenaltyCountType:
        counts = defaultdict(int)
        for action in self.received_actions:

            try:
                action = PlayerActionState[action.action_type]
                counts[action] += 1
            except KeyError:
                continue

        return {
            PlayerActionState.KICK.name: counts[PlayerActionState.KICK],
            PlayerActionState.PUNISH.name: counts[PlayerActionState.PUNISH],
            PlayerActionState.TEMPBAN.name: counts[PlayerActionState.TEMPBAN],
            PlayerActionState.PERMABAN.name: counts[PlayerActionState.PERMABAN],
        }

    def get_total_playtime_seconds(self) -> int:
        total = 0

        for i, s in enumerate(self.sessions):
            if not s.end and s.start and i == 0:
                total += (datetime.now() - s.start).total_seconds()
            elif s.end and s.start:
                total += (s.end - s.start).total_seconds()

        return int(total)

    def get_current_playtime_seconds(self) -> int:
        if self.sessions:
            start = self.sessions[0].start or self.sessions[0].created
            return int((datetime.now() - start).total_seconds())
        return 0

    def to_dict(self, limit_sessions=5) -> PlayerProfileType:
        blacklists = [record.to_dict() for record in self.blacklists]
        return {
            "id": self.id,
            PLAYER_ID: self.player_id,
            "created": self.created,
            "names": [name.to_dict() for name in self.names],
            "sessions": [session.to_dict() for session in self.sessions][
                :limit_sessions
            ],
            "sessions_count": len(self.sessions),
            "total_playtime_seconds": self.get_total_playtime_seconds(),
            "current_playtime_seconds": self.get_current_playtime_seconds(),
            "received_actions": [action.to_dict() for action in self.received_actions],
            "penalty_count": self.get_penalty_count(),
            "blacklists": blacklists,
            "is_blacklisted": any(record["is_active"] for record in blacklists),
            "flags": [f.to_dict() for f in (self.flags or [])],
            "watchlist": self.watchlist.to_dict() if self.watchlist else None,
            "steaminfo": self.steaminfo.to_dict() if self.steaminfo else None,
            "vips": [v.to_dict() for v in self.vips],
        }

    def __str__(self) -> str:
        aka = " | ".join([n.name for n in self.names])
        return f"{self.player_id} {aka}"


class SteamInfo(Base):
    __tablename__ = "steam_info"

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id_id: Mapped[int] = mapped_column(
        "playersteamid_id",
        ForeignKey("steam_id_64.id"),
        nullable=False,
        index=True,
        unique=True,
    )
    created: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated: Mapped[datetime] = mapped_column(onupdate=datetime.utcnow)
    profile: Mapped[SteamPlayerSummaryType] = mapped_column(default=JSONB.NULL)
    country: Mapped[str | None] = mapped_column(index=True)
    bans: Mapped[SteamBansType] = mapped_column(default=JSONB.NULL)

    player: Mapped[PlayerID] = relationship(back_populates="steaminfo")

    @property
    def has_bans(self):
        return any(
            self.bans.get(k)
            for k in [
                "VACBanned",
                "NumberOfVACBans",
                "DaysSinceLastBan",
                "NumberOfGameBans",
            ]
            if self.bans
        )

    def to_dict(self) -> SteamInfoType:
        return {
            "id": self.id,
            "created": self.created,
            "updated": self.updated,
            "profile": self.profile,
            "country": self.country if self.country else None,
            "bans": self.bans,
            "has_bans": self.has_bans,
        }


class WatchList(Base):
    __tablename__ = "player_watchlist"

    id: Mapped[int] = mapped_column(primary_key=True)
    modified: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    player_id_id: Mapped[int] = mapped_column(
        "playersteamid_id",
        ForeignKey("steam_id_64.id"),
        nullable=False,
        index=True,
        unique=True,
    )
    is_watched: Mapped[bool] = mapped_column(nullable=False)
    reason: Mapped[str] = mapped_column(default="")
    by: Mapped[str] = mapped_column()
    count: Mapped[int] = mapped_column(default=0)

    player: Mapped[PlayerID] = relationship(back_populates="watchlist")

    def to_dict(self) -> WatchListType:
        return {
            "id": self.id,
            "modified": self.modified,
            PLAYER_ID: self.player.player_id,
            "is_watched": self.is_watched,
            "reason": self.reason,
            "by": self.by,
            "count": self.count,
        }


class UserConfig(Base):
    __tablename__ = "user_config"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(unique=True, index=True)
    # TODO: Fix this on the UI settings branch once merged
    value: Mapped[dict[str, Any]] = mapped_column()


class PlayerFlag(Base):
    __tablename__ = "player_flags"
    __table_args__ = (
        UniqueConstraint("playersteamid_id", "flag", name="unique_flag_player_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id_id: Mapped[int] = mapped_column(
        "playersteamid_id", ForeignKey("steam_id_64.id"), nullable=False, index=True
    )
    flag: Mapped[str] = mapped_column(nullable=False, index=True)
    comment: Mapped[str] = mapped_column(String, nullable=True)
    modified: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    player: Mapped[PlayerID] = relationship(back_populates="flags")

    def to_dict(self) -> PlayerFlagType:
        return {
            "id": self.id,
            "flag": self.flag,
            "comment": self.comment,
            "modified": self.modified,
        }


class PlayerOptins(Base):
    __tablename__ = "player_optins"
    __table_args__ = (
        UniqueConstraint(
            "playersteamid_id", "optin_name", name="unique_optins_player_id"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id_id: Mapped[int] = mapped_column(
        "playersteamid_id", ForeignKey("steam_id_64.id"), nullable=False, index=True
    )
    optin_name: Mapped[str] = mapped_column(nullable=False, index=True)
    optin_value: Mapped[str] = mapped_column(nullable=True)
    modified: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    player: Mapped[PlayerID] = relationship(back_populates="optins")

    def to_dict(self) -> PlayerOptinsType:
        return {
            "id": self.id,
            "optin_name": self.optin_name,
            "optin_value": self.optin_value,
            "modified": self.modified,
        }


class PlayerName(Base):
    __tablename__ = "player_names"
    __table_args__ = (
        UniqueConstraint("playersteamid_id", "name", name="unique_name_steamid"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id_id: Mapped[int] = mapped_column(
        "playersteamid_id", ForeignKey("steam_id_64.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(nullable=False)
    created: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    last_seen: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    player: Mapped[PlayerID] = relationship(back_populates="names")

    def to_dict(self) -> PlayerNameType:
        return {
            "id": self.id,
            "name": self.name,
            PLAYER_ID: self.player.player_id,
            "created": self.created,
            "last_seen": self.last_seen,
        }


class PlayerSession(Base):
    __tablename__ = "player_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id_id: Mapped[int] = mapped_column(
        "playersteamid_id", ForeignKey("steam_id_64.id"), nullable=False, index=True
    )
    start: Mapped[datetime] = mapped_column()
    end: Mapped[datetime] = mapped_column()
    created: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    server_number: Mapped[int] = mapped_column()
    server_name: Mapped[str] = mapped_column()

    player: Mapped[PlayerID] = relationship(back_populates="sessions")

    def to_dict(self) -> PlayerSessionType:
        return {
            "id": self.id,
            PLAYER_ID: self.player.player_id,
            "start": self.start,
            "end": self.end,
            "created": self.created,
        }


class PlayersAction(Base):
    __tablename__ = "players_actions"

    id: Mapped[int] = mapped_column(primary_key=True)
    action_type: Mapped[str] = mapped_column(nullable=False)
    player_id_id: Mapped[int] = mapped_column(
        "playersteamid_id", ForeignKey("steam_id_64.id"), nullable=False, index=True
    )
    reason: Mapped[str] = mapped_column()
    by: Mapped[str] = mapped_column()
    time: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    player: Mapped[PlayerID] = relationship(back_populates="received_actions")

    def to_dict(self) -> PlayerActionType:
        return {
            "action_type": self.action_type,
            "reason": self.reason,
            "by": self.by,
            "time": self.time,
        }


class LogLine(Base):
    __tablename__ = "log_lines"
    __table_args__ = (UniqueConstraint("event_time", "raw", name="unique_log_line"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    version: Mapped[int] = mapped_column(default=1)
    creation_time: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    event_time: Mapped[datetime] = mapped_column(nullable=False, index=True)
    type: Mapped[str] = mapped_column(nullable=True)
    player1_name: Mapped[str] = mapped_column(nullable=True)
    player1_player_id: Mapped[int] = mapped_column(
        "player1_steamid", ForeignKey("steam_id_64.id"), nullable=True, index=True
    )
    player2_name: Mapped[str] = mapped_column(nullable=True)
    player2_player_id: Mapped[int] = mapped_column(
        "player2_steamid", ForeignKey("steam_id_64.id"), nullable=True, index=True
    )
    weapon: Mapped[str] = mapped_column()
    raw: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column()
    player_1: Mapped[PlayerID] = relationship(foreign_keys=[player1_player_id])
    player_2: Mapped[PlayerID] = relationship(foreign_keys=[player2_player_id])
    server: Mapped[str] = mapped_column()

    def get_weapon(self) -> str | None:
        if self.weapon:
            return self.weapon
        # Backward compatibility for logs before weapon was added
        if self.type and self.type.lower() in ("kill", "team kill"):
            try:
                return self.raw.rsplit(" with ", 1)[-1]
            except:
                logger.exception("Unable to extract weapon")

        return None

    def to_dict(self) -> DBLogLineType:
        # TODO: Fix typing
        return {
            "id": self.id,
            "version": self.version,
            "creation_time": self.creation_time,
            "event_time": self.event_time,
            "type": self.type,
            "player1_name": self.player1_name,
            "player1_id": self.player_1.player_id if self.player_1 else None,
            "player2_name": self.player2_name,
            "player2_id": self.player_2.player_id if self.player_2 else None,
            "raw": self.raw,
            "content": self.content,
            "server": self.server,
            "weapon": self.get_weapon(),
        }

    def compatible_dict(self) -> StructuredLogLineWithMetaData:
        # TODO: Add typing
        return {
            "version": self.version,
            "timestamp_ms": int(self.event_time.timestamp() * 1000),
            "event_time": self.event_time,
            "relative_time_ms": None,  # TODO
            "raw": self.raw,
            "line_without_time": None,  # TODO
            "action": self.type,
            "player_name_1": self.player1_name,
            "player_id_1": self.player_1.player_id if self.player_1 else None,
            "player_name_2": self.player2_name,
            "player_id_2": self.player_2.player_id if self.player_2 else None,
            "weapon": self.get_weapon(),
            "message": self.content,
            "sub_content": None,  # TODO
        }


class Maps(Base):
    __tablename__ = "map_history"
    __table_args__ = (
        UniqueConstraint(
            "start", "end", "server_number", "map_name", name="unique_map"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    creation_time: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    start: Mapped[datetime] = mapped_column(nullable=False, index=True)
    end: Mapped[datetime] = mapped_column(index=True)
    server_number: Mapped[int] = mapped_column(index=True)
    map_name: Mapped[str] = mapped_column(nullable=False, index=True)
    # A dict with the result of the game mapped as Axis=int, Allied=int
    result: Mapped[dict[str, int]] = mapped_column(nullable=True)

    player_stats: Mapped[list["PlayerStats"]] = relationship(back_populates="map")

    def to_dict(self, with_stats=False) -> MapsType:
        return {
            "id": self.id,
            "creation_time": self.creation_time,
            "start": self.start,
            "end": self.end,
            "server_number": self.server_number,
            "map_name": self.map_name,
            "result": (
                {
                    "axis": self.result.get("Axis"),
                    "allied": self.result.get("Allied"),
                }
                if self.result is not None and self.result.get("Allied") is not None
                else None
            ),
            "player_stats": (
                []
                if not with_stats or not self.player_stats
                else [s.to_dict() for s in self.player_stats]
            ),
        }


class PlayerStats(Base):
    __tablename__ = "player_stats"
    __table_args__ = (
        UniqueConstraint("playersteamid_id", "map_id", name="unique_map_player"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id_id: Mapped[int] = mapped_column(
        "playersteamid_id", ForeignKey("steam_id_64.id"), nullable=False, index=True
    )
    map_id: Mapped[int] = mapped_column(
        ForeignKey("map_history.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column()
    kills: Mapped[int] = mapped_column()
    kills_streak: Mapped[int] = mapped_column()
    deaths: Mapped[int] = mapped_column()
    deaths_without_kill_streak: Mapped[int] = mapped_column()
    teamkills: Mapped[int] = mapped_column()
    teamkills_streak: Mapped[int] = mapped_column()
    deaths_by_tk: Mapped[int] = mapped_column()
    deaths_by_tk_streak: Mapped[int] = mapped_column()
    nb_vote_started: Mapped[int] = mapped_column()
    nb_voted_yes: Mapped[int] = mapped_column()
    nb_voted_no: Mapped[int] = mapped_column()
    time_seconds: Mapped[int] = mapped_column()
    kills_per_minute: Mapped[float] = mapped_column()
    deaths_per_minute: Mapped[float] = mapped_column()
    kill_death_ratio: Mapped[float] = mapped_column()
    longest_life_secs: Mapped[int] = mapped_column()
    shortest_life_secs: Mapped[int] = mapped_column()
    combat: Mapped[int] = mapped_column()
    offense: Mapped[int] = mapped_column()
    defense: Mapped[int] = mapped_column()
    support: Mapped[int] = mapped_column()
    most_killed: Mapped[dict[str, int]] = mapped_column()
    death_by: Mapped[dict[str, int]] = mapped_column()
    weapons: Mapped[dict[str, int]] = mapped_column()
    death_by_weapons: Mapped[dict[str, int]] = mapped_column()

    player: Mapped[PlayerID] = relationship(
        foreign_keys=[player_id_id], back_populates="stats"
    )
    map: Mapped[Maps] = relationship(back_populates="player_stats")

    def to_dict(self) -> PlayerStatsType:
        # TODO: Fix typing
        return {
            "id": self.id,
            PLAYER_ID: self.player.player_id,
            "player": self.name,
            "steaminfo": (
                self.player.steaminfo.to_dict()
                if self.player and self.player.steaminfo
                else None
            ),
            "map_id": self.map_id,
            "kills": self.kills,
            "kills_streak": self.kills_streak,
            "deaths": self.deaths,
            "deaths_without_kill_streak": self.deaths_without_kill_streak,
            "teamkills": self.teamkills,
            "teamkills_streak": self.teamkills_streak,
            "deaths_by_tk": self.deaths_by_tk,
            "deaths_by_tk_streak": self.deaths_by_tk_streak,
            "nb_vote_started": self.nb_vote_started,
            "nb_voted_yes": self.nb_voted_yes,
            "nb_voted_no": self.nb_voted_no,
            "time_seconds": self.time_seconds,
            "kills_per_minute": self.kills_per_minute,
            "deaths_per_minute": self.deaths_per_minute,
            "kill_death_ratio": self.kill_death_ratio,
            "longest_life_secs": self.longest_life_secs,
            "shortest_life_secs": self.shortest_life_secs,
            "combat": self.combat,
            "offense": self.offense,
            "defense": self.defense,
            "support": self.support,
            "most_killed": self.most_killed,
            "death_by": self.death_by,
            "weapons": self.weapons,
            "death_by_weapons": self.death_by_weapons,
        }


class PlayerComment(Base):
    __tablename__ = "player_comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    creation_time: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    by: Mapped[str] = mapped_column()
    player_id_id: Mapped[int] = mapped_column(
        "playersteamid_id", ForeignKey("steam_id_64.id"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(nullable=False)

    player: Mapped[PlayerID] = relationship(back_populates="comments")

    def to_dict(self) -> PlayerCommentType:
        return {
            "id": self.id,
            "creation_time": self.creation_time,
            "player_id": self.player.player_id,
            "content": self.content,
            "by": self.by,
        }


class ServerCount(Base):
    __tablename__ = "server_counts"
    __table_args__ = (
        UniqueConstraint("server_number", "datapoint_time", name="unique_server_count"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    server_number: Mapped[int] = mapped_column()
    creation_time: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    datapoint_time: Mapped[datetime] = mapped_column(TIMESTAMP, unique=True, index=True)
    map_id: Mapped[int] = mapped_column(
        ForeignKey("map_history.id"), nullable=False, index=True
    )
    count: Mapped[int] = mapped_column(nullable=False)
    vip_count: Mapped[int] = mapped_column(nullable=False)
    players: Mapped["PlayerAtCount"] = relationship(back_populates="data_point")
    map: Mapped[Maps] = relationship(lazy="joined")

    def to_dict(self, players_as_tuple=False, with_player_list=True) -> ServerCountType:
        players = []

        if with_player_list and self.players:
            for p in self.players:
                p = p.to_dict()
                if players_as_tuple:
                    players.append((p["name"], p[PLAYER_ID], p["vip"]))
                else:
                    players.append(p)

        # TODO: Fix typing
        return {
            "server_number": self.server_number,
            "minute": self.datapoint_time,
            "count": self.count,
            "players": self.players,
            "map": self.map.map_name,
            "vip_count": self.vip_count,
        }


class PlayerAtCount(Base):
    __tablename__ = "player_at_count"
    __table_args__ = (
        UniqueConstraint(
            "playersteamid_id", "servercount_id", name="unique_player_at_count"
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    player_id_id: Mapped[int] = mapped_column(
        "playersteamid_id", ForeignKey("steam_id_64.id"), nullable=False, index=True
    )
    servercount_id: Mapped[int] = mapped_column(
        ForeignKey("server_counts.id"), nullable=False, index=True
    )
    vip: Mapped[bool] = mapped_column()
    data_point: Mapped[ServerCount] = relationship(back_populates="players")
    player: Mapped[PlayerID] = relationship(lazy="joined")

    def to_dict(self) -> PlayerAtCountType:
        try:
            name = self.player.names[0].name
        except:
            logger.exception("Unable to load name for %s", self.player.player_id)
            name = ""

        return {
            PLAYER_ID: self.player.player_id,
            "name": name,
            "vip": self.vip,
        }


class PlayerVIP(Base):
    __tablename__: str = "player_vip"
    __table_args__ = (
        UniqueConstraint(
            "playersteamid_id", "server_number", name="unique_player_server_vip"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    expiration: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )
    # Not making this unique (even though it should be) to avoid breaking existing CRCONs
    server_number: Mapped[int] = mapped_column()

    player_id_id: Mapped[int] = mapped_column(
        "playersteamid_id", ForeignKey("steam_id_64.id"), nullable=False, index=True
    )

    player: Mapped[PlayerID] = relationship(back_populates="vips")

    def to_dict(self) -> PlayerVIPType:
        return {
            "server_number": self.server_number,
            "expiration": self.expiration,
        }


class AuditLog(Base):
    __tablename__: str = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False, index=True)
    creation_time: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.utcnow
    )
    # Not making this unique (even though it should be) to avoid breaking existing CRCONs
    command: Mapped[str] = mapped_column(nullable=False, index=True)
    command_arguments: Mapped[str] = mapped_column()
    command_result: Mapped[str] = mapped_column()

    def to_dict(self) -> AuditLogType:
        return {
            "id": self.id,
            "username": self.username,
            "creation_time": self.creation_time,
            "command": self.command,
            "command_arguments": self.command_arguments,
            "command_result": self.command_result,
        }


class Blacklist(Base):
    __tablename__: str = "blacklist"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    sync: Mapped[BlacklistSyncMethod] = mapped_column(
        Enum(BlacklistSyncMethod), default=BlacklistSyncMethod.KICK_ONLY
    )
    servers: Mapped[Optional[int]]

    records: Mapped[list["BlacklistRecord"]] = relationship(
        back_populates="blacklist", cascade="all, delete"
    )

    def get_server_numbers(self) -> Optional[set[int]]:
        if self.servers is None:
            return None

        return mask_to_server_numbers(self.servers)

    def set_server_numbers(self, server_numbers: Sequence[int] | None):
        if server_numbers is None:
            self.set_all_servers()
        else:
            self.servers = server_numbers_to_mask(*server_numbers)

    def set_all_servers(self):
        self.servers = None

    @overload
    def to_dict(self, with_records: Literal[True]) -> BlacklistWithRecordsType: ...
    @overload
    def to_dict(self, with_records: Literal[False]) -> BlacklistType: ...
    @overload
    def to_dict(self, with_records: bool = False) -> BlacklistType: ...

    def to_dict(self, with_records: bool = False) -> BlacklistType:
        res = {
            "id": self.id,
            "name": self.name,
            "sync": self.sync.value,
            "servers": (
                None if self.servers is None else list(self.get_server_numbers())
            ),
        }
        if with_records:
            res["records"] = [
                record.to_dict(with_blacklist=False) for record in self.records
            ]
        return res


class BlacklistRecord(Base):
    __tablename__: str = "blacklist_record"
    id: Mapped[int] = mapped_column(primary_key=True)
    reason: Mapped[str]
    admin_name: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(tz=timezone.utc)
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))

    player_id_id: Mapped[int] = mapped_column(
        ForeignKey("steam_id_64.id"), nullable=False, index=True
    )
    blacklist_id: Mapped[int] = mapped_column(
        ForeignKey("blacklist.id", ondelete="CASCADE"), nullable=False, index=True
    )

    player: Mapped["PlayerID"] = relationship(back_populates="blacklists")
    blacklist: Mapped["Blacklist"] = relationship(back_populates="records")

    def expires_in(self):
        if not self.expires_at:
            return None
        return self.expires_at - datetime.now(tz=timezone.utc)

    def is_expired(self):
        if not self.expires_at:
            return None
        return self.expires_at <= datetime.now(tz=timezone.utc)

    def get_formatted_reason(self):
        variables = {
            "player_id": self.player.player_id,
            "player_name": self.player.names[0].name if self.player.names else "",
            "banned_at": self.created_at.strftime("%d %b %H:%M"),
            "banned_until": (
                self.expires_at.strftime("%d %b %H:%M")
                if self.expires_at
                else "forever"
            ),
            "expires_at": (
                self.expires_at.strftime("%d %b %H:%M") if self.expires_at else "never"
            ),
            "duration": (
                humanize_timedelta(self.expires_at - self.created_at)
                if self.expires_at
                else "forever"
            ),
            "expires": humanize_timedelta(self.expires_at).replace("forever", "never"),
            "ban_id": self.id,
            "admin_name": self.admin_name,
            "blacklist_name": self.blacklist.name,
        }
        return self.reason.format_map(SafeStringFormat(**variables))

    # I know this isn't entirely representative but I cba to add 4 different types, 3 is already more than enough
    @overload
    def to_dict(
        self, with_blacklist: Literal[True] = True, with_player: Literal[False] = False
    ) -> BlacklistRecordWithBlacklistType: ...
    @overload
    def to_dict(
        self, with_blacklist: Literal[True] = True, with_player: Literal[True] = False
    ) -> BlacklistRecordWithPlayerType: ...
    @overload
    def to_dict(
        self, with_blacklist: Literal[False] = True, with_player: bool = False
    ) -> BlacklistRecordType: ...

    def to_dict(
        self, with_blacklist: bool = True, with_player: bool = False
    ) -> BlacklistRecordWithBlacklistType:
        res = {
            "id": self.id,
            "player_id": self.player.player_id,
            "reason": self.reason,
            "admin_name": self.admin_name,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "is_active": not self.is_expired(),
        }

        if with_blacklist:
            res["blacklist"] = self.blacklist.to_dict(with_records=False)

        if with_player:
            res["player"] = {
                "id": self.player.id,
                "player_id": self.player.player_id,
                "created": self.player.created,
                "names": [name.to_dict() for name in self.player.names],
                "steaminfo": (
                    self.player.steaminfo.to_dict() if self.player.steaminfo else None
                ),
            }
            res["formatted_reason"] = self.get_formatted_reason()

        return res


def install_unaccent():
    with enter_session() as sess:
        sess.execute(text("CREATE EXTENSION IF NOT EXISTS unaccent;"))


def get_session_maker() -> sessionmaker:
    engine = get_engine()
    sess = sessionmaker()
    sess.configure(bind=engine)
    return sess


@contextmanager
def enter_session() -> Generator[Session, None, None]:
    session_maker = get_session_maker()

    try:
        sess: Session = session_maker()
        yield sess
        # Only commit if there were no exceptions, otherwise rollback
        sess.commit()
    except (ProgrammingError, InvalidRequestError) as e:
        logger.exception(e)
        sess.rollback()
    finally:
        sess.close()


# TODO: This probably belongs in rcon.types
class LogLineWebHookField(pydantic.BaseModel):
    """A Discord Webhook URL and optional roles to ping for log events and applicable servers

    LOG_LINE_WEBHOOKS in config.yml
    """

    url: str
    mentions: Optional[List[str]] = []
    servers: List[str] = []

    @pydantic.field_validator("mentions")
    def valid_role(cls, values):
        if not values:
            return []

        for role_or_user in values:
            if not re.search(r"<@&\d+>|<@\d+>", role_or_user):
                print(f"Invalid Discord role or user {role_or_user}")
                raise ValueError(f"Invalid Discord role {role_or_user}")

        return values
