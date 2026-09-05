"""
FastAPI Application Entrypoint for Quantitative Portfolio Optimization & Live Paper Trading Platform.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.models.database import init_db
from backend.app.api.routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Quant Platform Database & Models...")
    init_db()
    logger.info(f"System started in {'DEBUG' if settings.DEBUG else 'PRODUCTION'} mode.")
    yield
    logger.info("Shutting down Quant Platform Engine.")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Institutional Quantitative Portfolio Optimization, Walk-Forward Backtesting, and Live/Paper Trading with Upstox API v2",
    lifespan=lifespan
)

# CORS configuration for React Vite frontend (running on http://localhost:5173 or other ports)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {
        "status": "ONLINE",
        "service": settings.APP_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "api_endpoints": "/api"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "upstox_configured": bool(settings.UPSTOX_API_KEY)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
