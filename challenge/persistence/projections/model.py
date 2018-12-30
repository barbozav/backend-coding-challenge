from sqlalchemy import TEXT, VARCHAR, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from challenge.persistence import Base
from challenge.persistence.eventstore.model import AggregateModel


class TranslationModel(Base):
    __tablename__ = 'translations'

    uuid = Column(
        VARCHAR(36),
        ForeignKey('aggregates.uuid'),
        primary_key=True,
    )
    status = Column(VARCHAR(16))
    length = Column(Integer)
    text = Column(TEXT)
    translated_text = Column(TEXT)
    aggregate = relationship(AggregateModel)
