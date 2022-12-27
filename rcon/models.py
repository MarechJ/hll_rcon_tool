import logging
import os
import re
from contextlib import contextmanager
from curses import echo
from datetime import datetime
from operator import index
from typing import List, Optional, TypedDict

import pydantic
from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.orm.session import object_session
from sqlalchemy.schema import UniqueConstraint

from rcon.types import (
    AuditLogType,
    BlackListType,
    DBLogLineType,
    MapsType,
    PlayerActionType,
    PlayerAtCountType,
    PlayerCommentType,
    PlayerFlagType,
    PlayerNameType,
    PlayerOptinsType,
    PlayerProfileType,
    PlayerSessionType,
    PlayerStatsType,
    ServerCountType,
    UserConfigType,
    WatchListType,
)

logger = logging.getLogger(__name__)

_ENGINE = None


def get_engine():
    global _ENGINE

    if _ENGINE:
        return _ENGINE
    url = os.getenv("DB_URL")
    if not url:
        msg = "No $DB_URL specified. Can't use database features"
        logger.error(msg)
        raise ValueError(msg)

    _ENGINE = create_engine(url, echo=False)
    return _ENGINE


Base = declarative_base()


class PlayerSteamID(Base):
    __tablename__ = "steam_id_64"
    id = Column(Integer, primary_key=True)
    steam_id_64 = Column(String, nullable=False, index=True, unique=True)
    created = Column(DateTime, default=datetime.utcnow)
    names = relationship(
        "PlayerName",
        backref="steamid",
        uselist=True,
        order_by="nullslast(desc(PlayerName.last_seen))",
    )
    # If you ever change the ordering of sessions make sure you change the playtime calc code
    sessions = relationship(
        "PlayerSession",
        backref="steamid",
        uselist=True,
        order_by="desc(PlayerSession.created)",
    )
    received_actions = relationship(
        "PlayersAction",
        backref="steamid",
        uselist=True,
        order_by="desc(PlayersAction.time)",
    )
    blacklist = relationship("BlacklistedPlayer", backref="steamid", uselist=False)
    flags = relationship("PlayerFlag", backref="steamid")
    watchlist = relationship("WatchList", backref="steamid", uselist=False)
    steaminfo = relationship("SteamInfo", backref="steamid", uselist=False)
    comments = relationship("PlayerComment", back_populates="player")
    stats = relationship("PlayerStats", backref="steamid", uselist=False)

    vips = relationship(
        "PlayerVIP",
        back_populates="steamid",
        uselist=True,
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    optins = relationship("PlayerOptins", backref="steamid", uselist=True)

    @property
    def server_number(self):
        return int(os.getenv("SERVER_NUMBER"))

    @hybrid_property
    def vip(self):
        return (
            object_session(self)
            .query(PlayerVIP)
            .filter(
                PlayerVIP.playersteamid_id == self.id,
                PlayerVIP.server_number == self.server_number,
            )
            .one_or_none()
        )

    def get_penalty_count(self):
        penalities_type = {"KICK", "PUNISH", "TEMPBAN", "PERMABAN"}
        counts = dict.fromkeys(penalities_type, 0)
        for action in self.received_actions:
            if action.action_type in penalities_type:
                counts[action.action_type] += 1

        return counts

    def get_total_playtime_seconds(self):
        total = 0

        for i, s in enumerate(self.sessions):
            if not s.end and s.start and i == 0:
                total += (datetime.now() - s.start).total_seconds()
            elif s.end and s.start:
                total += (s.end - s.start).total_seconds()

        return int(total)

    def get_current_playtime_seconds(self):
        if self.sessions:
            start = self.sessions[0].start or self.sessions[0].created
            return int((datetime.now() - start).total_seconds())
        return 0

    def to_dict(self, limit_sessions=5) -> PlayerProfileType:
        return dict(
            id=self.id,
            steam_id_64=self.steam_id_64,
            created=self.created,
            names=[name.to_dict() for name in self.names],
            sessions=[session.to_dict() for session in self.sessions][:limit_sessions],
            sessions_count=len(self.sessions),
            total_playtime_seconds=self.get_total_playtime_seconds(),
            current_playtime_seconds=self.get_current_playtime_seconds(),
            received_actions=[action.to_dict() for action in self.received_actions],
            penalty_count=self.get_penalty_count(),
            blacklist=self.blacklist.to_dict() if self.blacklist else None,
            flags=[f.to_dict() for f in (self.flags or [])],
            watchlist=self.watchlist.to_dict() if self.watchlist else None,
            steaminfo=self.steaminfo.to_dict() if self.steaminfo else None,
        )

    def __str__(self):
        aka = " | ".join([n.name for n in self.names])
        return f"{self.steam_id_64} {aka}"


class SteamInfo(Base):
    __tablename__ = "steam_info"

    id = Column(Integer, primary_key=True)
    playersteamid_id = Column(
        Integer, ForeignKey("steam_id_64.id"), nullable=False, index=True, unique=True
    )
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, onupdate=datetime.utcnow)
    profile = Column(JSONB)
    country = Column(String, index=True)
    bans = Column(JSONB)

    def to_dict(self):
        return dict(
            id=self.id,
            created=self.created,
            updated=self.updated,
            profile=self.profile,
            country=self.country,
            bans=self.bans,
        )


class WatchList(Base):
    __tablename__ = "player_watchlist"

    id = Column(Integer, primary_key=True)
    playersteamid_id = Column(
        Integer, ForeignKey("steam_id_64.id"), nullable=False, index=True, unique=True
    )
    is_watched = Column(Boolean, nullable=False)
    reason = Column(String, default="")
    comment = Column(String, default="")

    def to_dict(self) -> WatchListType:
        return dict(
            id=self.id,
            steam_id_64=self.steamid.steam_id_64,
            is_watched=self.is_watched,
            reason=self.reason,
            comment=self.comment,
        )


class UserConfig(Base):
    __tablename__ = "user_config"

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, index=True)
    value = Column(JSONB)

    def to_dict(self) -> UserConfigType:
        return {self.key: self.value}


class PlayerFlag(Base):
    __tablename__ = "player_flags"
    __table_args__ = (UniqueConstraint("playersteamid_id", "flag", name="unique_flag_steamid"),)

    id = Column(Integer, primary_key=True)
    playersteamid_id = Column(Integer, ForeignKey("steam_id_64.id"), nullable=False, index=True)
    flag = Column(String, nullable=False, index=True)
    comment = Column(String, nullable=True)
    modified = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> PlayerFlagType:
        return dict(id=self.id, flag=self.flag, comment=self.comment, modified=self.modified)


class PlayerOptins(Base):
    __tablename__ = "player_optins"
    __table_args__ = (
        UniqueConstraint("playersteamid_id", "optin_name", name="unique_optins_steamid"),
    )

    id = Column(Integer, primary_key=True)
    playersteamid_id = Column(Integer, ForeignKey("steam_id_64.id"), nullable=False, index=True)
    optin_name = Column(String, nullable=False, index=True)
    optin_value = Column(String, nullable=True)
    modified = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> PlayerOptinsType:
        return dict(
            id=self.id,
            optin_name=self.optin_name,
            optin_value=self.optin_value,
            modified=self.modified,
        )


class PlayerName(Base):
    __tablename__ = "player_names"
    __table_args__ = (UniqueConstraint("playersteamid_id", "name", name="unique_name_steamid"),)

    id = Column(Integer, primary_key=True)
    playersteamid_id = Column(Integer, ForeignKey("steam_id_64.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    created = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> PlayerNameType:
        return dict(
            id=self.id,
            name=self.name,
            steam_id_64=self.steamid.steam_id_64,
            created=self.created,
            last_seen=self.last_seen,
        )


class PlayerSession(Base):
    __tablename__ = "player_sessions"

    id = Column(Integer, primary_key=True)
    playersteamid_id = Column(Integer, ForeignKey("steam_id_64.id"), nullable=False, index=True)
    start = Column(DateTime)
    end = Column(DateTime)
    created = Column(DateTime, default=datetime.utcnow)
    server_number = Column(Integer)
    server_name = Column(String)

    def to_dict(self) -> PlayerSessionType:
        return dict(
            id=self.id,
            steam_id_64=self.steamid.steam_id_64,
            start=self.start,
            end=self.end,
            created=self.created,
        )


class BlacklistedPlayer(Base):
    __tablename__ = "player_blacklist"

    id = Column(Integer, primary_key=True)
    playersteamid_id = Column(
        Integer, ForeignKey("steam_id_64.id"), nullable=False, index=True, unique=True
    )
    is_blacklisted = Column(Boolean, default=False)
    reason = Column(String)
    by = Column(String)

    def to_dict(self) -> BlackListType:
        return dict(
            steam_id_64=self.steamid.steam_id_64,
            is_blacklisted=self.is_blacklisted,
            reason=self.reason,
            by=self.by,
        )


class PlayersAction(Base):
    __tablename__ = "players_actions"

    id = Column(Integer, primary_key=True)
    action_type = Column(String, nullable=False)
    playersteamid_id = Column(
        Integer,
        ForeignKey("steam_id_64.id"),
        nullable=False,
        index=True,
    )
    reason = Column(String)
    by = Column(String)
    time = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> PlayerActionType:
        return dict(action_type=self.action_type, reason=self.reason, by=self.by, time=self.time)


class LogLine(Base):
    __tablename__ = "log_lines"
    __table_args__ = (UniqueConstraint("event_time", "raw", name="unique_log_line"),)

    id = Column(Integer, primary_key=True)
    version = Column(Integer, default=1)
    creation_time = Column(TIMESTAMP, default=datetime.utcnow)
    event_time = Column(DateTime, nullable=False, index=True)
    type = Column(String, nullable=True)
    player1_name = Column(String, nullable=True)
    player1_steamid = Column(
        Integer,
        ForeignKey("steam_id_64.id"),
        nullable=True,
        index=True,
    )
    player2_name = Column(String, nullable=True)
    player2_steamid = Column(
        Integer,
        ForeignKey("steam_id_64.id"),
        nullable=True,
        index=True,
    )
    weapon = Column(String)
    raw = Column(String, nullable=False)
    content = Column(String)
    steamid1 = relationship("PlayerSteamID", foreign_keys=[player1_steamid])
    steamid2 = relationship("PlayerSteamID", foreign_keys=[player2_steamid])
    server = Column(String)

    def get_weapon(self):
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
        return dict(
            id=self.id,
            version=self.version,
            creation_time=self.creation_time,
            event_time=self.event_time,
            type=self.type,
            player_name=self.player1_name,
            player1_id=self.player1_steamid,
            player2_name=self.player2_name,
            player2_id=self.player2_steamid,
            raw=self.raw,
            content=self.content,
            server=self.server,
            weapon=self.get_weapon(),
        )

    def compatible_dict(self):
        return {
            "id": self.id,
            "version": self.version,
            "timestamp_ms": int(self.event_time.timestamp() * 1000),
            "event_time": self.event_time,
            "relative_time_ms": None,  # TODO
            "raw": self.raw,
            "line_without_time": None,  # TODO
            "action": self.type,
            "player": self.player1_name,
            "steam_id_64_1": self.steamid1.steam_id_64 if self.steamid1 else None,
            "player1_id": self.player1_steamid,
            "player2_id": self.player2_steamid,
            "player2": self.player2_name,
            "steam_id_64_2": self.steamid2.steam_id_64 if self.steamid2 else None,
            "weapon": self.get_weapon(),
            "message": self.content,
            "sub_content": None,  # TODO
        }


class Maps(Base):
    __tablename__ = "map_history"
    __table_args__ = (
        UniqueConstraint("start", "end", "server_number", "map_name", name="unique_map"),
    )

    id = Column(Integer, primary_key=True)

    creation_time = Column(TIMESTAMP, default=datetime.utcnow)
    start = Column(DateTime, nullable=False, index=True)
    end = Column(DateTime, index=True)
    server_number = Column(Integer, index=True)
    map_name = Column(String, nullable=False, index=True)

    player_stats = relationship("PlayerStats", backref="map", uselist=True)

    def to_dict(self, with_stats=False) -> MapsType:
        return dict(
            id=self.id,
            creation_time=self.creation_time,
            start=self.start,
            end=self.end,
            server_number=self.server_number,
            map_name=self.map_name,
            player_stats=[]
            if not with_stats or not self.player_stats
            else [s.to_dict() for s in self.player_stats],
        )


class PlayerStats(Base):
    __tablename__ = "player_stats"
    __table_args__ = (UniqueConstraint("playersteamid_id", "map_id", name="unique_map_player"),)

    id = Column(Integer, primary_key=True)
    playersteamid_id = Column(
        Integer,
        ForeignKey("steam_id_64.id"),
        nullable=False,
        index=True,
    )
    map_id = Column(
        Integer,
        ForeignKey("map_history.id"),
        nullable=False,
        index=True,
    )
    name = Column(String)
    kills = Column(Integer)
    kills_streak = Column(Integer)
    deaths = Column(Integer)
    deaths_without_kill_streak = Column(Integer)
    teamkills = Column(Integer)
    teamkills_streak = Column(Integer)
    deaths_by_tk = Column(Integer)
    deaths_by_tk_streak = Column(Integer)
    nb_vote_started = Column(Integer)
    nb_voted_yes = Column(Integer)
    nb_voted_no = Column(Integer)
    time_seconds = Column(Integer)
    kills_per_minute = Column(Float)
    deaths_per_minute = Column(Float)
    kill_death_ratio = Column(Float)
    longest_life_secs = Column(Integer)
    shortest_life_secs = Column(Integer)
    most_killed = Column(JSONB)
    death_by = Column(JSONB)
    weapons = Column(JSONB)

    def to_dict(self) -> PlayerStatsType:
        return dict(
            id=self.id,
            player_id=self.playersteamid_id,
            player=self.name,
            steaminfo=self.steamid.steaminfo.to_dict() if self.steamid.steaminfo else None,
            map_id=self.map_id,
            kills=self.kills,
            kills_streak=self.kills_streak,
            deaths=self.deaths,
            deaths_without_kill_streak=self.deaths_without_kill_streak,
            teamkills=self.teamkills,
            teamkills_streak=self.teamkills_streak,
            deaths_by_tk=self.deaths_by_tk,
            deaths_by_tk_streak=self.deaths_by_tk_streak,
            nb_vote_started=self.nb_vote_started,
            nb_voted_yes=self.nb_voted_yes,
            nb_voted_no=self.nb_voted_no,
            time_seconds=self.time_seconds,
            kills_per_minute=self.kills_per_minute,
            deaths_per_minute=self.deaths_per_minute,
            kill_death_ratio=self.kill_death_ratio,
            longest_life_secs=self.longest_life_secs,
            shortest_life_secs=self.shortest_life_secs,
            most_killed=self.most_killed,
            death_by=self.death_by,
            weapons=self.weapons,
        )


class PlayerComment(Base):
    __tablename__ = "player_comments"
    id = Column(Integer, primary_key=True)
    creation_time = Column(TIMESTAMP, default=datetime.utcnow)
    by = Column(String)
    playersteamid_id = Column(
        Integer,
        ForeignKey("steam_id_64.id"),
        nullable=False,
        index=True,
    )
    content = Column(String, nullable=False)

    player = relationship("PlayerSteamID", back_populates="comments")

    def to_dict(self) -> PlayerCommentType:
        return dict(
            id=self.id,
            creation_time=self.creation_time,
            playersteamid_id=self.playersteamid_id,
            content=self.content,
            by=self.by,
        )


class ServerCount(Base):
    __tablename__ = "server_counts"
    __table_args__ = (
        UniqueConstraint("server_number", "datapoint_time", name="unique_server_count"),
    )
    id = Column(Integer, primary_key=True)
    server_number = Column(Integer)
    creation_time = Column(TIMESTAMP, default=datetime.utcnow)
    datapoint_time = Column(TIMESTAMP, unique=True, index=True)
    map_id = Column(
        Integer,
        ForeignKey("map_history.id"),
        nullable=False,
        index=True,
    )
    count = Column(Integer, nullable=False)
    vip_count = Column(Integer, nullable=False)
    players = relationship("PlayerAtCount", back_populates="data_point")
    map = relationship("Maps", lazy="joined")

    def to_dict(self, players_as_tuple=False, with_player_list=True) -> ServerCountType:
        players = []

        if with_player_list and self.players:
            for p in self.players:
                p = p.to_dict()
                if players_as_tuple:
                    players.append((p["name"], p["steam_id_64"], p["vip"]))
                else:
                    players.append(p)

        return dict(
            server_number=self.server_number,
            minute=self.datapoint_time,
            count=self.count,
            players=players,
            map=self.map.map_name,
            vip_count=self.vip_count,
        )


class PlayerAtCount(Base):
    __tablename__ = "player_at_count"
    __table_args__ = (
        UniqueConstraint("playersteamid_id", "servercount_id", name="unique_player_at_count"),
    )
    id = Column(Integer, primary_key=True)
    playersteamid_id = Column(
        Integer,
        ForeignKey("steam_id_64.id"),
        nullable=False,
        index=True,
    )
    servercount_id = Column(
        Integer,
        ForeignKey("server_counts.id"),
        nullable=False,
        index=True,
    )
    vip = Column(Boolean)
    data_point = relationship("ServerCount", back_populates="players")
    steamid = relationship("PlayerSteamID", lazy="joined")

    def to_dict(self) -> PlayerAtCountType:
        try:
            name = self.steamid.names[0].name
        except:
            logger.exception("Unable to load name for %s", self.steamid.steam_id_64)
            name = ""
        return dict(steam_id_64=self.steamid.steam_id_64, name=name, vip=self.vip)


class PlayerVIP(Base):
    __tablename__: str = "player_vip"
    __table_args__ = (
        UniqueConstraint("playersteamid_id", "server_number", name="unique_player_server_vip"),
    )

    id = Column(Integer, primary_key=True)
    expiration = Column(TIMESTAMP(timezone=True), nullable=False)
    # Not making this unique (even though it should be) to avoid breaking existing CRCONs
    server_number = Column(Integer)

    playersteamid_id = Column(
        Integer,
        ForeignKey("steam_id_64.id"),
        nullable=False,
        index=True,
    )

    steamid = relationship("PlayerSteamID", back_populates="vips")


class AuditLog(Base):
    __tablename__: str = "audit_log"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, index=True)
    creation_time = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    # Not making this unique (even though it should be) to avoid breaking existing CRCONs
    command = Column(String, nullable=False, index=True)
    command_arguments = Column(String)
    command_result = Column(String)

    def to_dict(self) -> AuditLogType:
        return dict(
            id=self.id,
            username=self.username,
            creation_time=self.creation_time,
            command=self.command,
            command_arguments=self.command_arguments,
            command_result=self.command_result,
        )


def init_db(force=False):
    # create tables
    engine = get_engine()
    if force is True:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def install_unaccent():
    with enter_session() as sess:
        sess.execute("CREATE EXTENSION IF NOT EXISTS unaccent;")


def get_session_maker():
    engine = get_engine()
    sess = sessionmaker()
    sess.configure(bind=engine)
    return sess


@contextmanager
def enter_session():
    sess = get_session_maker()

    try:
        sess = sess()
        yield sess
    finally:
        sess.commit()
        sess.close()


class LogLineWebHookField(pydantic.BaseModel):
    """A Discord Webhook URL and optional roles to ping for log events and applicable servers

    LOG_LINE_WEBHOOKS in config.yml
    """

    url: str
    mentions: Optional[List[str]] = []
    servers: List[str] = []

    @pydantic.validator("mentions")
    def valid_role(cls, values):
        if not values:
            return []

        for role_or_user in values:
            if not re.search(r"<@&\d+>|<@\d+>", role_or_user):
                print(f"Invalid Discord role or user {role_or_user}")
                raise ValueError(f"Invalid Discord role {role_or_user}")

        return values
