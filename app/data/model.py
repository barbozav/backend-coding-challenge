from app import db


class AggregateModel(db.Model):
    __tablename__ = 'aggregates'
    uuid = db.Column(db.VARCHAR(36), primary_key=True)
    version = db.Column(db.Integer, default=1)


class EventModel(db.Model):
    __tablename__ = 'events'

    uuid = db.Column(db.VARCHAR(36), primary_key=True)
    event = db.Column(db.VARCHAR(36))
    data = db.Column(db.JSON)

    aggregate_uuid = db.Column(
        db.VARCHAR(36), db.ForeignKey('aggregates.uuid'))
    aggregate = db.relationship(AggregateModel, backref='events')
