from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
import time

# Configure logging on startup
configure_logging()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration=process_time,
        client_ip=request.client.host
    )
    
    return response

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Temporarily allow all for development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

from app.api.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    try:
        from app.core.database import init_db
        await init_db()
        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connections on shutdown."""
    try:
        from app.core.database import close_db
        await close_db()
        logger.info("Application shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

@app.get("/")
def root():
    return {"message": "Welcome to AI Help Desk API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
