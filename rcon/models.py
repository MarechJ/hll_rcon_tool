from datetime import datetime
import logging
import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint


logger = logging.getLogger(__name__)

_ENGINE = None

def get_engine():
    global _ENGINE

    if _ENGINE:
        return _ENGINE
    url = os.getenv('DB_URL')
    if not url:
        url = 'sqlite:///rcon.db'
        logger.warning("No $DB_URL specified, falling back to SQLlite in rundir")
    
    _ENGINE = create_engine(url)
    return _ENGINE

Base = declarative_base()

class PlayerSteamID(Base):
    __tablename__ = 'steam_id_64'
    id = Column(Integer, primary_key=True)
    steam_id_64  = Column(String, nullable=False, index=True, unique=True)
    created = Column(DateTime, default=datetime.utcnow)
    names = relationship("PlayerName", backref="steamid", uselist=True)

class PlayerName(Base):
    __tablename__ = 'player_names'
    __table_args__ = (UniqueConstraint('playersteamid_id', 'name', name='unique_name_steamid'),)

    id = Column(Integer, primary_key=True)
    playersteamid_id = Column(Integer, ForeignKey('steam_id_64.id'), nullable=False)
    name = Column(String, nullable=False)
    created = Column(DateTime, default=datetime.utcnow)
    

def init_db():
    # create tables
    engine = get_engine()
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
