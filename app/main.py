import logging 
from fastapi import FastAPI
from app.core.config import get_settings
from app.core.logging import setup_logging
from fastapi.responses import JSONResponse
from app.core.exceptions import AppException
from app.core.middleware import RequestIDMiddleware
from app.api.v1.ingestion import router as ingestion_router

setup_logging()

logger = logging.getLogger(__name__)
settings = get_settings()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description = "Production-oriented RAG Backend Services"
)

app.include_router(
    ingestion_router,
    prefix="/api/v1",
)

app.add_middleware(RequestIDMiddleware)

@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    logger.error(
        "Application error | code=%s | message=%s",
        exc.code,
        exc.message,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        },
    )

@app.on_event("startup")
async def startup_event():
    logger.info(f"Application started")



@app.get("/health")
async def health_check():
    logger.info("Health check endpoint called") 

    return {
        "status":"healthy",
        "service":settings.app_name,
        "version" : settings.app_version,
        "environment" : settings.environment,
    }