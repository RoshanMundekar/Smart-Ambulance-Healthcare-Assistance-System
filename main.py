"""
Smart Ambulance & Healthcare Assistance System
FastAPI Application Entry Point
"""
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse, FileResponse
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

            # Dynamic migration: ensure hospital_id exists in users table
            from sqlalchemy import text
            with engine.begin() as conn:
                columns_result = conn.execute(text("SHOW COLUMNS FROM users LIKE 'hospital_id'")).fetchone()
                if not columns_result:
                    logger.info("Database migration: adding hospital_id column to users table...")
                    conn.execute(text("ALTER TABLE users ADD COLUMN hospital_id INT NULL"))
                    conn.execute(text("ALTER TABLE users ADD CONSTRAINT fk_users_hospital FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE SET NULL"))
                    logger.info("Database migration: hospital_id column and foreign key constraint added successfully.")
        except Exception as e:
            logger.error(f"Table creation/migration error: {e}")
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
# Static Files & Templates
# ============================================================
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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


@app.get("/sw.js", include_in_schema=False)
def serve_sw():
    return FileResponse("static/sw.js", media_type="application/javascript")


# ============================================================
# Page Routes  (HTML)
# ============================================================
@app.get("/", include_in_schema=False)
def landing_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", include_in_schema=False)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/dashboard", include_in_schema=False)
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/consultation", include_in_schema=False)
def consultation_page(request: Request):
    return templates.TemplateResponse("consultation.html", {"request": request})


@app.get("/driver", include_in_schema=False)
def driver_page(request: Request):
    return templates.TemplateResponse("driver.html", {"request": request})


@app.get("/hospital", include_in_schema=False)
def hospital_page(request: Request):
    return templates.TemplateResponse("hospital.html", {"request": request})


@app.get("/admin", include_in_schema=False)
def admin_page(request: Request):
    response = templates.TemplateResponse("admin.html", {"request": request})
    # Prevent browser from caching this page so the role-guard JS is always fresh
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    return response


# ============================================================
# Health Check
# ============================================================
@app.get("/info", tags=["Health"])
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


# ============================================================
# TWA Digital Asset Links (required for Android TWA APK)
# Allows the APK to run without the browser address bar.
# After building the APK, replace the placeholder fingerprint
# with the real SHA-256 from your keystore.
# ============================================================
@app.get("/.well-known/assetlinks.json", include_in_schema=False)
def asset_links():
    package_name = os.getenv("TWA_PACKAGE_NAME", "com.smartambulance.healthcare")
    fingerprint = os.getenv(
        "TWA_SHA256_FINGERPRINT",
        "00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00",
    )
    return JSONResponse([
        {
            "relation": ["delegate_permission/common.handle_all_urls"],
            "target": {
                "namespace": "android_app",
                "package_name": package_name,
                "sha256_cert_fingerprints": [fingerprint],
            },
        }
    ])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true",
        workers=1 if os.getenv("DEBUG", "False").lower() == "true" else int(os.getenv("WORKERS", 4)),
    )
