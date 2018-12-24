class AggregateModel(Base):
    __tablename__ = 'aggregates'

    uuid = Column(VARCHAR(36), primary_key=True)
    version = Column(Integer, default=1)


class EventModel(Base):
    __tablename__ = 'events'

    uuid = Column(VARCHAR(36), primary_key=True)
    aggregate_uuid = Column(VARCHAR(36), ForeignKey('aggregates.uuid'))
    status = Column(VARCHAR(16))
    data = Column(JSON)

    aggregate = relationship(AggregateModel, uselist=False, backref='events')
