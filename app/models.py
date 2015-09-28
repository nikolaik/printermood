from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from app.db import get_or_create
from app.lifx_api import get_lights


Base = declarative_base()


class Face(Base):
    __tablename__ = 'faces'

    id = Column(Integer, primary_key=True)
    # TODO
    # image = 'blob'
    # created = 'auto_now_created'
    # updated = 'auto_now_updated'
    # emotions = 'json'
    emotions = Column(String(250))


class Light(Base):
    __tablename__ = 'lights'

    id = Column(Integer, primary_key=True)
    power_state = Column(String(250))

    @staticmethod
    def sync_lights():
        _lights = get_lights()

        for l in _lights:
            l_local = get_or_create(Light, id=l['id'])
            print(l_local)
            # TODO
