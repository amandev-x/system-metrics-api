from pydantic import BaseModel, Field 
from datetime import datetime
from typing import Optional

class MetricResponse(BaseModel):
    id: Optional[int] = None 
    timestamp: datetime
    cpu_percent: float = Field(..., description="CPU usage percentage", ge=0, le=100)
    memory_percent: float = Field(..., description="Memory usage percentage", ge=0, le=100)
    disk_percent: float = Field(..., description="Disk usage percentage", ge=0, le=100)
    network_sent_mb: float = Field(..., description="Network data sent in MB", ge=0, le=100)
    network_recv_mb: float = Field(..., description="Network data received in MB", ge=0, le=100)
    hostname: str 

    class Config:
        from_attributes = True

class HealthResponse(BaseModel):
    status: str 
    timestamp: datetime
    version: str 
    database: str 

class APIResponseInfo(BaseModel):
    name: str 
    version: str 
    description: str 
    endpoints: dict 