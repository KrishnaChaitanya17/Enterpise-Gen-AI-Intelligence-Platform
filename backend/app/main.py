from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.middleware import RequestIDMiddleware
from app.core.exceptions import global_exception_handler
from app.core.logging import logger

from app.api.routes_auth import router as auth_router
from app.api.routes_chat import router as chat_router
from app.api.metrics import router as metrics_router
from app.api.routes_admin import router as admin_router
from app.ai.router.analytics_routes import router as analytics_router

from app.api.admin.health import router as health_router
from app.api.admin.dashboard import router as dashboard_router

# --------------------------------------------------
# Lifespan — startup & shutdown hooks
# --------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🚀 {settings.APP_NAME} starting up | ENV={settings.ENV}")
    yield
    logger.info("🛑 Shutting down — cleaning up resources")


# --------------------------------------------------
# App factory
# --------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs" if settings.ENV != "production" else None,   # hide Swagger in prod
    redoc_url=None,
    lifespan=lifespan,
)


# --------------------------------------------------
# CORS  ✅ FIX: was completely missing
# --------------------------------------------------
ALLOWED_ORIGINS = [
    "http://localhost:5173",   # Vite dev server
    "http://localhost:3000",
]

if settings.ENV == "production":
    # Replace with your real domain
    ALLOWED_ORIGINS = ["https://your-production-domain.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Middleware
# --------------------------------------------------
app.add_middleware(RequestIDMiddleware)


# --------------------------------------------------
# Global exception handler
# --------------------------------------------------
app.add_exception_handler(Exception, global_exception_handler)


# --------------------------------------------------
# Routers
# --------------------------------------------------
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(metrics_router)
app.include_router(admin_router)
app.include_router(analytics_router)


# --------------------------------------------------
# Health check  ✅ FIX: was missing
# --------------------------------------------------
@app.get("/health", tags=["System"])
async def health_check():
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "app": settings.APP_NAME,
            "env": settings.ENV,
            "version": "1.0.0",
        },
    )


# --------------------------------------------------
# Root
# --------------------------------------------------
@app.get("/", tags=["System"])
async def root():
    return {"message": f"Welcome to {settings.APP_NAME}"}


app.include_router(health_router)
app.include_router(dashboard_router)