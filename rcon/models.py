from datetime import datetime
import logging
import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

logger = logging.getLogger(__name__)

_ENGINE = None


def get_engine():
    global _ENGINE

    if _ENGINE:
        return _ENGINE
    url = os.getenv('DB_URL')
    if not url:
        msg = "No $DB_URL specified. Can't use database features"
        logger.error(msg)
        raise ValueError(msg)

    _ENGINE = create_engine(url)
    return _ENGINE


Base = declarative_base()


class PlayerSteamID(Base):
    __tablename__ = 'steam_id_64'
    id = Column(Integer, primary_key=True)
    steam_id_64 = Column(String, nullable=False, index=True, unique=True)
    created = Column(DateTime, default=datetime.utcnow)
    names = relationship("PlayerName", backref="steamid",
                         uselist=True, order_by="desc(PlayerName.created)")
    # If you ever change the ordering of sessions make sure you change the playtime calc code
    sessions = relationship("PlayerSession", backref="steamid",
                            uselist=True, order_by="desc(PlayerSession.created)")
    received_actions = relationship("PlayersAction", backref="steamid",
                                    uselist=True, order_by="desc(PlayersAction.time)")
    blacklist = relationship("BlacklistedPlayer", backref="steamid",
                             uselist=False)
    flags = relationship("PlayerFlag", backref="steamid")

    def get_penalty_count(self):
        penalities_type = {'KICK', 'PUNISH', 'TEMPBAN', 'PERMABAN'}
        counts = dict.fromkeys(penalities_type, 0)
        for action in self.received_actions:
            if action.action_type in penalities_type:
                counts[action.action_type] +=  1

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
            return int((datetime.now() - self.sessions[0].start).total_seconds())
        return 0

    def to_dict(self, limit_sessions=5):
        return dict(
            id=self.id,
            steam_id_64=self.steam_id_64,
            created=self.created,
            names=[name.to_dict() for name in self.names],
            sessions=[session.to_dict()
                      for session in self.sessions][:limit_sessions],
            sessions_count=len(self.sessions),
            total_playtime_seconds=self.get_total_playtime_seconds(),
            current_playtime_seconds=self.get_current_playtime_seconds(),
            received_actions=[
                action.to_dict()
                for action in self.received_actions
            ],
            penalty_count=self.get_penalty_count(),
            blacklist=self.blacklist.to_dict() if self.blacklist else None,
            flags=[f.to_dict() for f in (self.flags or [])]
        )

    def __str__(self):
        aka = ' | '.join([n.name for n in self.names])
        return f"{self.steam_id_64} {aka}"


class UserConfig(Base):
    __tablename__ = 'user_config'

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, index=True)
    value = Column(JSONB)

    def to_dict(self):
        return {
            self.key: self.value
        }
        

class PlayerFlag(Base):
    __tablename__ = 'player_flags'
    __table_args__ = (UniqueConstraint('playersteamid_id',
                                       'flag', name='unique_flag_steamid'),)

    id = Column(Integer, primary_key=True)
    playersteamid_id = Column(Integer, ForeignKey(
        'steam_id_64.id'), nullable=False, index=True)
    flag = Column(String, nullable=False, index=True)
    comment = Column(String, nullable=True)
    modified = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return dict(
            id=self.id,
            flag=self.flag,
            commment=self.comment,
            modified=self.modified
        )


class PlayerName(Base):
    __tablename__ = 'player_names'
    __table_args__ = (UniqueConstraint('playersteamid_id',
                                       'name', name='unique_name_steamid'),)

    id = Column(Integer, primary_key=True)
    playersteamid_id = Column(Integer, ForeignKey(
        'steam_id_64.id'), nullable=False, index=True)
    name = Column(String, nullable=False)
    created = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            steam_id_64=self.steamid.steam_id_64,
            created=self.created
        )


class PlayerSession(Base):
    __tablename__ = 'player_sessions'

    id = Column(Integer, primary_key=True)
    playersteamid_id = Column(Integer, ForeignKey(
        'steam_id_64.id'), nullable=False, index=True)
    start = Column(DateTime)
    end = Column(DateTime)
    created = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return dict(
            id=self.id,
            steam_id_64=self.steamid.steam_id_64,
            start=self.start,
            end=self.end,
            created=self.created
        )


class BlacklistedPlayer(Base):
    __tablename__ = 'player_blacklist'

    id = Column(Integer, primary_key=True)
    playersteamid_id = Column(
        Integer, ForeignKey('steam_id_64.id'),
        nullable=False, index=True,
        unique=True
    )
    is_blacklisted = Column(Boolean, default=False)
    reason = Column(String)

    def to_dict(self):
        return dict(
            steam_id_64=self.steamid.steam_id_64,
            is_blacklisted=self.is_blacklisted,
            reason=self.reason
        )


class PlayersAction(Base):
    __tablename__ = 'players_actions'

    id = Column(Integer, primary_key=True)
    action_type = Column(String, nullable=False)
    playersteamid_id = Column(
        Integer, ForeignKey('steam_id_64.id'),
        nullable=False, index=True,
    )
    reason = Column(String)
    by = Column(String)
    time = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return dict(
            action_type=self.action_type,
            reason=self.reason,
            by=self.by,
            time=self.time
        )

def init_db(force=False):
    # create tables
    engine = get_engine()
    if force is True:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


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
