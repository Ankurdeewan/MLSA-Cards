from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from .config import get_settings
from .routers import auth, game
from .database import engine
from .models import Base

settings = get_settings()
app = FastAPI(title="Game Collectible API")

# Create database tables
Base.metadata.create_all(bind=engine)

app.add_middleware(SessionMiddleware, secret_key=settings.jwt_secret)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(game.router)

from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")

from .schemas import HealthResponse

@app.get("/health", response_model=HealthResponse)
async def health():
    return {"status": "ok"}
from fastapi.openapi.utils import get_openapi

from fastapi.responses import FileResponse

@app.get("/home.html")
def serve_home():
    return FileResponse("static/home.html")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Game Collectible API",
        version="0.1.0",
        description="API for authentication and game endpoints",
        routes=app.routes,
    )

    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    # Apply global security
    openapi_schema["security"] = [{"BearerAuth": []}]

    # Remove security from /health
    if "/health" in openapi_schema["paths"]:
        for method in openapi_schema["paths"]["/health"].values():
            method.pop("security", None)

    # Assign schema
    app.openapi_schema = openapi_schema
    return app.openapi_schema
app.openapi = custom_openapi