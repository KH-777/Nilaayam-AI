from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from backend.routers import documents, agreements, properties, legal, reports
from backend.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Nilaayam AI starting up...")
    logger.info(f"Environment: {settings.app_env}")
    yield
    logger.info("Nilaayam AI shutting down...")

app = FastAPI(
    title="Nilaayam AI API",
    description="Intelligent Agreement & Property Registration Risk Scanner for Tamil Nadu",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router, prefix="/api", tags=["Documents"])
app.include_router(agreements.router, prefix="/api", tags=["Agreements"])
app.include_router(properties.router, prefix="/api", tags=["Properties"])
app.include_router(legal.router, prefix="/api", tags=["Legal References"])
app.include_router(reports.router, prefix="/api", tags=["Reports"])

@app.get("/")
def root():
    return {"message": "Nilaayam AI API", "version": "1.0.0", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "nilaayam-ai"}
