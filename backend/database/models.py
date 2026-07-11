from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime

from database.database_config import Base

class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(String, index=True, nullable=False)
    
    prediction_value = Column(Float, nullable=False)
    
    timestamp = Column(DateTime, default = datetime.utcnow)

