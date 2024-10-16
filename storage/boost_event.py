from sqlalchemy import Column, Integer, String, DateTime
from base import Base
from datetime import datetime

class BoostEvent(Base):
    __tablename__ = 'boost_events'
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(String(250), nullable=False)
    boost_amount = Column(Integer, nullable=False)
    total_boost = Column(Integer, nullable=False)
    location = Column(String(100), nullable=False)
    trace_id = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def to_dict(self):
        """Converts the BoostEvent object into a dictionary."""
        return {
            'id': self.id,
            'trace_id': self.trace_id,
            'player_id': self.player_id,
            'boost_amount': self.boost_amount,
            'total_boost': self.total_boost,
            'location': self.location,
            'date_created': self.date_created.strftime("%Y-%m-%dT%H:%M:%S")
        }
