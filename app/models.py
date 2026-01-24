from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
import os 
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Databse Settings
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./metrics.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

Sessionlocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Base class for our models
Base = declarative_base()

class SystemMetric(Base):
    __tablename__ = "system_metrics"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    cpu_percent = Column(Float)
    memory_percent = Column(Float)
    disk_percent = Column(Float)
    network_sent_mb = Column(Float)
    network_recv_mb = Column(Float)
    hostname = Column(String)

def init_db():
    """ Initialize database tables """
    Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()



