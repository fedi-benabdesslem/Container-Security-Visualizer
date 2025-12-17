#!/usr/bin/env python3
# main.py - FastAPI application entry point

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from backend.config import config
from backend.database import init_db, engine
from backend.utils.logger import logger


# Import routers
from sqlalchemy import text
from backend.api import events, query, stats, alerts, containers, websocket, analytics



@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events - runs on startup and shutdown
    """
    # Startup
    logger.info("🚀 Starting Container Security Visualizer Backend...")
    logger.info(f"Server: {config.server.host}:{config.server.port}")
    logger.info(f"Database: {config.database.type} at {config.database.host}")

    # Initialize database
    try:
        init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("🛑 Shutting down backend...")
    engine.dispose()
    logger.info("✅ Database connections closed")


# Create FastAPI app
app = FastAPI(
    title="Container Security Visualizer API",
    description="Real-time container security monitoring backend",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors.allow_origins,
    allow_credentials=config.cors.allow_credentials,
    allow_methods=config.cors.allow_methods,
    allow_headers=config.cors.allow_headers,
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if config.server.debug else None
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "version": "0.1.0"
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Container Security Visualizer API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


# Include routers
app.include_router(events.router, prefix="/api", tags=["events"])
app.include_router(query.router, prefix="/api", tags=["query"])
app.include_router(stats.router, prefix="/api", tags=["statistics"])
app.include_router(alerts.router, prefix="/api", tags=["alerts"])
app.include_router(containers.router, prefix="/api", tags=["containers"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])
app.include_router(analytics.router, prefix="/api", tags=["analytics"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=config.server.host,
        port=config.server.port,
        reload=config.server.reload,
        log_level="info"
    )
