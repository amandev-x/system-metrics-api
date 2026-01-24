from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
import os 
from dotenv import load_dotenv
from app.routes import router
from app.models import init_db

load_dotenv()

app = FastAPI(
    title = os.getenv("APP_NAME", "System Metrics API"),
    description = "Production-ready system metrics collection API with nginx reverse proxy",
    version = os.getenv("APP_VERSION", "1.0.0"),
    docs_url = "/docs",
    redoc_url = "/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],    # Allow all origins. In production, restrict to specific domains
    allow_credentials = True,
    allow_methods = ["*"],    # Allow GET, POST, PUT, DELETE, etc.
    allow_headers = ["*"]     # Allow all headers
)

# Include routes
app.include_router(router, tags=["metrics"])

# Startup event to initialize database
@app.on_event("startup")     # Use lifespan event  in FastAPI 0.95+
async def startup_event():
  print("Starting system metrics API...")
  init_db()
  print("Database initialized")
  print(f"API documentation available at: http:/localhost:8000/docs")

# Shutdown event 
@app.on_event("shutdown")
async def shutdown():
   print("Shutting down system metrics API...")
  
  
