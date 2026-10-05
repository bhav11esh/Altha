"""
OpenWebUI Medical Backend Service
Serves API endpoints for the medical web interface
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MediAI OpenWebUI Backend",
    description="Backend service for medical web interface",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    service: str
    uptime: float

class AppConfig(BaseModel):
    name: str
    version: str
    api_base: str
    environment: str

# Routes
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "openwebui-backend",
        "uptime": 0
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "MediAI OpenWebUI Backend",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/config", response_model=AppConfig)
async def get_config():
    """Get application configuration"""
    return {
        "name": "MediAI",
        "version": "1.0.0",
        "api_base": os.getenv("API_INTEGRATION_URL", "http://api-integration:8003"),
        "environment": os.getenv("NODE_ENV", "production")
    }

@app.get("/api/info")
async def get_info():
    """Get application info"""
    return {
        "name": "MediAI Medical AI Platform",
        "version": "1.0.0",
        "services": {
            "conversation": os.getenv("CONVERSATION_SERVICE_URL", "http://conversation-service:8002"),
            "api_integration": os.getenv("API_INTEGRATION_URL", "http://api-integration:8003"),
            "crewai": os.getenv("CREWAI_URL", "http://crewai:8001")
        }
    }

@app.get("/api/status")
async def get_status():
    """Get system status"""
    return {
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "connected",
            "cache": "connected",
            "ai_backend": "ready"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
