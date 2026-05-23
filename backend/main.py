"""
Smart Ambulance & Healthcare Assistance System
FastAPI Application Entry Point
"""
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

# Configure logger
os.makedirs("logs", exist_ok=True)
logger.add("logs/app.log", rotation="10 MB", retention="30 days", level="INFO")

from app.database.connection import check_db_connection, engine, Base
from app.api.routes import (
    auth_router, emergency_router, appointments_router,
    driver_router, hospital_router, admin_router,
)
# Import all models to ensure they are registered
import app.models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Smart Ambulance & Healthcare System...")
    if check_db_connection():
        logger.info("Database connected successfully")
        # Create tables if they don't exist (for development)
        # In production use Alembic migrations instead
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables verified/created")
        except Exception as e:
            logger.error(f"Table creation error: {e}")
    else:
        logger.error("Database connection failed! Check your .env configuration.")
    yield
    logger.info("Shutting down Smart Ambulance System...")


app = FastAPI(
    title="Smart Ambulance & Healthcare Assistance System",
    description="""
    ## AI-Powered Emergency & Healthcare Platform

    ### Features:
    - **Emergency Ambulance Booking** — One-tap emergency with real-time tracking
    - **Doctor Consultation** — AI symptom analysis + specialist booking
    - **AI Symptom Analysis** — SpaCy NLP + ML-powered diagnosis
    - **Hospital Recommendation** — Distance, specialization, availability scoring
    - **Ambulance Allocation** — Nearest available unit with optimal routing
    - **Real-time Tracking** — WebSocket-based live updates
    - **Role-based Access** — Patient / Driver / Doctor / Hospital Admin / System Admin

    ### Authentication:
    Use `Bearer <token>` in the Authorization header after `/api/auth/login`.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ============================================================
# CORS
# ============================================================
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:5500,http://localhost:8080").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# API Routes
# ============================================================
API_PREFIX = "/api"

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(emergency_router, prefix=API_PREFIX)
app.include_router(appointments_router, prefix=API_PREFIX)
app.include_router(driver_router, prefix=API_PREFIX)
app.include_router(hospital_router, prefix=API_PREFIX)
app.include_router(admin_router, prefix=API_PREFIX)


# ============================================================
# Health Check
# ============================================================
@app.get("/", tags=["Health"])
def root():
    return {
        "name": "Smart Ambulance & Healthcare System",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    db_ok = check_db_connection()
    return JSONResponse(
        status_code=200 if db_ok else 503,
        content={
            "status": "healthy" if db_ok else "degraded",
            "database": "connected" if db_ok else "disconnected",
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true",
        workers=1 if os.getenv("DEBUG", "False").lower() == "true" else int(os.getenv("WORKERS", 4)),
    )
