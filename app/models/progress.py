from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from datetime import datetime
from app.db.database import Base

class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text_id = Column(Integer, ForeignKey("texts.id"), nullable=True)
    score = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    time_spent = Column(Float, default=0.0)  # segundos
    level = Column(String, default="En Inicio")
    points_earned = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class SyncEvent(Base):
    __tablename__ = "sync_events"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, nullable=False)
    event_type = Column(String, nullable=False)
    payload = Column(Text, nullable=False)  # JSON string
    synced = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)