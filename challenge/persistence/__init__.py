import sqlalchemy
from dynaconf import settings
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def create_db():
    db = sqlalchemy.create_engine(settings.DATABASE_URI)
    return db


def create_tables(db):
    Base.metadata.create_all(db)
