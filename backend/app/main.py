from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

import time
from sqlalchemy import text

from .config import get_settings
from .routers import auth, game
from .database import engine
from .models import Base


# Track when the service started (for uptime)
START_TIME = time.time()

settings = get_settings()
app = FastAPI(title="Game Collectible API")

# Create database tables if they don't exist
Base.metadata.create_all(bind=engine)

# Session + CORS middleware
app.add_middleware(SessionMiddleware, secret_key=settings.jwt_secret)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(game.router)


# -------- HEALTH ENDPOINT (must be BEFORE static mount) --------
@app.get("/health")
async def health():
    """
    Health + diagnostics endpoint.
    Useful for monitoring and deployment checks.
    """
    db_status = "unknown"

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_status = "connected"
    except Exception:
        db_status = "disconnected"

    uptime = round(time.time() - START_TIME, 2)

    return {
        "status": "ok",
        "service": "Game Collectible API",
        "database": db_status,
        "uptime_seconds": uptime,
        "version": "1.0.0",
    }


# STATIC FILES (must be AFTER /health)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
