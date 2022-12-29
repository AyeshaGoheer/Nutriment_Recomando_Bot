import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base

from constants import DATABASE_URI

engine = db.create_engine(DATABASE_URI)
Base = declarative_base()


class History(Base):
    __tablename__ = 'history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    request = db.Column(db.String)
    response = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f'<History(user_id={self.user_id}, request={self.request}, response={self.response}, timestamp={self.timestamp})>'


# Create the history table
Base.metadata.create_all(engine)
