from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.db.database import Base

class Text(Base):
    __tablename__ = "texts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    level = Column(String, nullable=False)  # En Inicio, En Proceso, Satisfactorio
    difficulty_score = Column(Integer, default=1)
    genre = Column(String, default="narrativo")
    created_at = Column(DateTime, default=datetime.utcnow)