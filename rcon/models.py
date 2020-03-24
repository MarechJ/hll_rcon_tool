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
        url = 'sqlite:///rcon.db'
        logger.warning(
            "No $DB_URL specified, falling back to SQLlite in rundir")

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
    sessions = relationship("PlayerSession", backref="steamid",
                            uselist=True, order_by="desc(PlayerSession.end)")
    blacklist = relationship("BlacklistedPlayer", backref="steamid",
                             uselist=False)

    def to_dict(self, limit_sessions=5):
        return dict(
            id=self.id,
            steam_id_64=self.steam_id_64,
            created=self.created,
            names=[name.to_dict() for name in self.names],
            sessions=[session.to_dict()
                      for session in self.sessions][:limit_sessions],
            blacklist=self.blacklist.to_dict() if self.blacklist else None
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
