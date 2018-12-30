from contextlib import contextmanager

import sqlalchemy
from dynaconf import settings
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
Session = sessionmaker()


def create_db(uri=None):
    uri = uri or settings.DATABASE_URI
    db = sqlalchemy.create_engine(uri)
    Session.configure(bind=db)
    return db


def create_tables(db):
    Base.metadata.create_all(db)


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except:  # noqa: E722
        session.rollback()
        raise
    finally:
        session.close()
