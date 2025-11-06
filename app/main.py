from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import logging

from . import models, schemas
from .database import get_db, engine
from .logging_config import setup_logging
from app.logger import log_execution

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

@app.get("/paintings", response_model=schemas.PaginatedResponse[schemas.PaintingResponse])
@log_execution("/paintings")
async def get_all_paintings(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Порядок сортировки по году"),
    artist_name: str = Query(None, description="Фильтр по фамилии художника (частичное совпадение)")
    ):
    try:
        skip = (page - 1) * page_size

        query = db.query(models.Painting)

        if artist_name:
            query = query.join(models.Artist).filter(models.Artist.artist_short_name.ilike(f"%{artist_name}%"))

        sort_direction = models.Painting.year.desc() if sort_order == "desc" else models.Painting.year.asc()

        paintings = query.order_by(sort_direction).offset(skip).limit(page_size).all()
        
        total = query.count()
        total_pages = (total + page_size - 1) // page_size
        
        return {
            "data": paintings,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }

    except Exception as e:          
        raise HTTPException(
            status_code=500, 
            detail="Ошибка при получении картин"
        )

@app.get("/paintings/{painting_id}", response_model=schemas.PaintingResponse)
@log_execution("/paintings/{painting_id}")
async def get_painting_by_id(painting_id: int, db: Session = Depends(get_db)):
    try:
        painting = db.query(models.Painting).filter(models.Painting.id == painting_id).first()
        
        if not painting:
            raise HTTPException(
                status_code=404,
                detail=f"Картина с ID {painting_id} не найдена"
            )
        
        return painting

    except HTTPException:
        raise
    except Exception as e:          
        raise HTTPException(
            status_code=500, 
            detail="Ошибка при получении картины"
        )