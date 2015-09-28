from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def create_db():
    from app import settings
    from app.models import Base

    engine = create_engine(settings.DB_ENGINE)
    Base.metadata.create_all(engine)


def get_db_session():
    from app import settings
    from app.models import Base

    engine = create_engine(settings.DB_ENGINE)
    Base.metadata.bind = engine
    DBSession = sessionmaker()
    DBSession.bind = engine

    return DBSession()


def get_or_create(model, **kwargs):
    session = get_db_session()
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance

if __name__ == '__main__':
    create_db()
