from fastapi import FastAPI
import logging

from .database import get_db
from .logging_config import setup_logging
from app.logger import log_execution
from app.routers import paintings

setup_logging()  
logger = logging.getLogger("app.main")

app = FastAPI(
    title="Art Gallery API",
    description="API для галереи картин",
    version="1.0.0"
)

@app.get("/")
@log_execution("root")
async def root():
    return {"message": "Добро пожаловать в Art Gallery API!"}

app.include_router(paintings.router)