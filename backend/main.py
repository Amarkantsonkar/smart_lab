from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict
import os
import logging

from config.settings import settings
from config.database import db, get_database
from src.auth import oauth2_scheme

app = FastAPI(
    title=settings.PROJECT_NAME, 
    description="API for managing lab power shutdown procedures",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception handler caught: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": {
                "message": "Internal server error",
                "type": "internal_error"
            }
        }
    )

# HTTP exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": {
                "message": exc.detail,
                "type": "http_error",
                "status_code": exc.status_code
            }
        }
    )

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Smart Lab Power Shutdown Assistant API")
    await db.connect_to_database()
    logger.info("Database connection established")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Smart Lab Power Shutdown Assistant API")
    await db.close_database_connection()
    logger.info("Database connection closed")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Smart Lab Power Shutdown Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Smart Lab Power Shutdown Assistant API",
        "version": "1.0.0",
        "users_api": "enabled"
    }

from src.api.v1.auth.router import router as auth_router
from src.api.v1.devices.router import router as devices_router
from src.api.v1.checklist.router import router as checklist_router
from src.api.v1.shutdown_logs.router import router as shutdown_logs_router
from src.api.v1.shutdown.router import router as shutdown_router
from src.api.v1.users.router import router as users_router

app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth")
app.include_router(devices_router, prefix=f"{settings.API_V1_STR}/devices")
app.include_router(checklist_router, prefix=f"{settings.API_V1_STR}/checklist")
app.include_router(shutdown_logs_router, prefix=f"{settings.API_V1_STR}/shutdown-logs")
app.include_router(shutdown_router, prefix=f"{settings.API_V1_STR}/shutdown")
app.include_router(users_router, prefix=f"{settings.API_V1_STR}/users")

@app.get("/test-users")
def test_users():
    return {"message": "Users API test endpoint"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)