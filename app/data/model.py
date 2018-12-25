from sqlalchemy import JSON, VARCHAR, Column, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class AggregateModel(Base):
    __tablename__ = 'aggregates'

    uuid = Column(VARCHAR(36), primary_key=True)
    version = Column(Integer, default=1)


class EventModel(Base):
    __tablename__ = 'events'

    uuid = Column(VARCHAR(36), primary_key=True)

    event = Column(VARCHAR(36))
    data = Column(JSON)

    aggregate_uuid = Column(VARCHAR(36), ForeignKey('aggregates.uuid'))
    aggregate = relationship(AggregateModel, backref='events')
