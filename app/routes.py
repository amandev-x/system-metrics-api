from fastapi import APIRouter, Depends, HTTPException, Header, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List
from datetime import timedelta, datetime, timezone
import os 

from app.models import SystemMetric, get_db
from app.schemas import MetricResponse, HealthResponse, APIResponseInfo
from app.services import metrics_collector

router = APIRouter()

# Security: Simple API key authentication
def verify_api_key(x_api_key: str = Header(...)):
    expected_key = os.getenv("API_KEY", "")

    if x_api_key != expected_key:
        raise HTTPException(
            status_code = 401,
            detail = "Invalid API Key"
        )
    return x_api_key

@router.get("/endpoint", dependencies=[Depends(verify_api_key)])
async def endpoint():
    return {"status": "success"}

@router.get("/", response_model=APIResponseInfo)
async def root():
    return {
        "name": os.getenv("APP_NAME", "System Metrics API"),
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "description": "Real time system metrics and monitoring API",
        "endpoints": {
            "health": "/health",
            "current_metrics": "/metrics/current",
            "collect_metrics": "/metrics/collect",
            "metrics_history": "/metrics/history",
            "latest_metrics": "/metrics/latest"
        }
    }

@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        raise HTTPException (
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE,
            detail = "Database Unavailable"
        )
    
    return {
        "status": "Healthy",
        "timestamp": datetime.now(),
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "database": db_status
    }

@router.get("/metrics/current", response_model = MetricResponse)
async def get_current_metrics():
    metrics = metrics_collector.collect_current_metrics()
    return MetricResponse(**metrics)  # FastAPI Converting Python Dict to JSON model for HTTP

@router.post("/metrics/collect", response_model=MetricResponse)
async def collect_metrics(db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
     try:
          metric = metrics_collector.save_metrics(db)
          return MetricResponse.model_validate(metric)
     except Exception as e:
          raise HTTPException(
              status_code = status.HTTP_503_SERVICE_UNAVAILABLE,
              detail = f"Failed to collect metrics: {str(e)}"
          )

@router.get("/metrics/latest", response_model=MetricResponse)
async def get_latest_metrics(db: Session = Depends(get_db)):
    metric = db.query(SystemMetric).order_by(SystemMetric.timestamp.desc()).first()
    if not metric:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "No metrics found"
        )
    return MetricResponse.model_validate(metric)

@router.get("/metrics/history", response_model=List[MetricResponse])
async def get_metrics_history(db: Session = Depends(get_db), 
                             hours: Optional[int] = Query(24, description="Number of hours to look back", ge=1, le=720),
                             limit: Optional[int] = Query(100, description="Maximum number of records to return", ge=1, le=1000)):
     # Time threshold
     time_threshold = datetime.now(timezone.utc) - timedelta(hours=hours)

     # Query the database with filtes
     metrics = db.query(SystemMetric).filter(SystemMetric.timestamp >= time_threshold).order_by(SystemMetric.timestamp.desc()).limit(limit).all()

     if not metrics:
          raise HTTPException(
              status_code = status.HTTP_404_NOT_FOUND,
              detail = f"No metrics found for the last {hours} hours"
          )

     return [MetricResponse.model_validate(metric)  for metric in metrics]


