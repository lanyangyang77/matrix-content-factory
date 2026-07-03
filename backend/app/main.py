"""FastAPI application entry point."""
from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import Base, engine
from app.routers.content import router as content_router
from app.routers.merchants import router as merchants_router
from app.routers.export import router as export_router

logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Matrix Biz Automation System",
    description="AI-driven multi-tenant closed-loop business automation API.",
    version="0.1.0",
    docs_url="/docs" if settings.app_env != "production" else None,
    redoc_url="/redoc" if settings.app_env != "production" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    try:
        logger.info("Creating database tables (if not exist)...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables ready.")
    except Exception as exc:
        logger.warning(
            "Database unavailable - tables not created (%s). API docs still work.",
            exc,
        )


app.include_router(content_router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "matrix-biz-api", "version": "0.1.0"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error_code": "INTERNAL_ERROR",
            "message": "An internal server error occurred.",
        },
    )
app.include_router(merchants_router)
app.include_router(export_router)
