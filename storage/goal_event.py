from sqlalchemy import Column, Integer, String, DateTime
from base import Base
from datetime import datetime

class GoalEvent(Base):
    __tablename__ = 'goal_events'
    id = Column(Integer, primary_key=True, autoincrement=True)
    trace_id = Column(String(250), nullable=False)
    player_id = Column(String(250), nullable=False)
    goal_speed = Column(Integer, nullable=False)
    goal_type = Column(String(100), nullable=False)
    goal_distance = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False)

    def to_dict(self):
        """Converts the GoalEvent object into a dictionary."""
        return {
            'id': self.id,
            'trace_id': self.trace_id,
            'player_id': self.player_id,
            'goal_speed': self.goal_speed,
            'goal_type': self.goal_type,
            'goal_distance': self.goal_distance,
            'date_created': self.date_created
        }
