import re
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import logging
import transliterate

from app import models, schemas
from app.dependencies import get_db
from app.logger import log_execution, get_logger

router = APIRouter(tags=["paintings"])
logger = get_logger("routers.paintings")

@router.get(
        "/paintings",
        response_model=schemas.PaginatedResponse[schemas.PaintingResponse],
        summary="Получить список картин",
        description="Возвращает paginated список всех картин с возможностью фильтрации и сортировки"
)
@log_execution("/paintings")
async def get_all_paintings(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Порядок сортировки по году"),
    artist_name: str = Query(None, description="Фильтр по фамилии художника (частичное совпадение)")
    ):
    """
    Получить список всех картин с пагинацией.

    Параметры:
    - **page**: Номер страницы (начинается с 1)
    - **page_size**: Количество картин на странице (1-100)
    - **sort_order**: Порядок сортировки по году создания ("asc" или "desc")
    - **artist_name**: Фильтр по фамилии художника (регистронезависимый поиск)

    Возвращает:
    - Paginated список картин с метаданными пагинации
    """
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
    
@router.get(
        "/paintings/{painting_id}",
        response_model=schemas.PaintingResponse,
        summary="Получить картину по ID",
        description="Возвращает детальную информацию о конкретной картине по её ID"
)
@log_execution("/paintings/{painting_id}")
async def get_painting_by_id(
    painting_id: int, db: Session = Depends(get_db)):
    """
    Получить детальную информацию о картине по её идентификатору.

    Параметры:
    - **painting_id**: ID картины (целое число)

    Возвращает:
    - Объект картины со всей информацией

    Исключения:
    - 404: Если картина с указанным ID не найдена
    - 500: При внутренней ошибке сервера
    """
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
    
@router.post(
        "/paintings",
        response_model=schemas.PaintingResponse,
        summary="Создать новую картину",
        description="Создает новую запись о картине в базе данных",
        status_code=201
)
@log_execution("create_painting")
async def create_painting(painting_data: schemas.PaintingCreate, db: Session = Depends(get_db)):
    """
    Создать новую картину в системе.

    Параметры:
    - **painting_data**: Данные для создания картины (объект PaintingCreate)

    Особенности:
    - Поле `unique_title` генерируется автоматически на основе названия и года
    - Проверяет существование указанных artist_id и museum_id

    Возвращает:
    - Созданный объект картины с присвоенным ID

    Исключения:
    - 404: Если указанный художник или музей не существуют
    - 500: При ошибке создания в базе данных
    """
    try:
        _check_artist_exists(painting_data.artist_id, db)
            
        _check_museum_exists(painting_data.museum_id, db)

        unique_title = _generate_painting_unique_title(
            title=painting_data.title,
            year=painting_data.year,
            db=db
        )
        
        painting_dict = painting_data.model_dump()
        painting_dict["unique_title"] = unique_title
        
        painting = models.Painting(**painting_dict)
        db.add(painting)
        db.commit()
        db.refresh(painting)
        return painting
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при создании картины")
    
@router.put(
        "/paintings/{painting_id}",
        response_model=schemas.PaintingResponse,
        summary="Обновить данные картины",
        description="Обновляет информацию о существующей картине (частичное обновление)"
)
@log_execution("update_painting")
async def update_painting(
    painting_id: int, 
    painting_data: schemas.PaintingUpdate, 
    db: Session = Depends(get_db)
):
    """
    Обновить информацию о существующей картине.

    Параметры:
    - **painting_id**: ID обновляемой картины
    - **painting_data**: Данные для обновления (только изменяемые поля)

    Особенности:
    - Поддерживает частичное обновление (только переданные поля)
    - При изменении названия или года автоматически генерируется новый unique_title
    - Проверяет существование новых artist_id и museum_id если они переданы

    Возвращает:
    - Обновленный объект картины

    Исключения:
    - 404: Если картина, художник или музей не найдены
    - 500: При ошибке обновления в базе данных
    """
    try:
        painting = db.query(models.Painting).filter(models.Painting.id == painting_id).first()
        if not painting:
            raise HTTPException(status_code=404, detail=f"Картина с ID {painting_id} не найдена")

        if painting_data.artist_id is not None:
            _check_artist_exists(painting_data.artist_id, db)
        
        if painting_data.museum_id is not None:
            _check_museum_exists(painting_data.museum_id, db)
        
        need_new_unique_title = (
            painting_data.title is not None and painting_data.title != painting.title or
            painting_data.year is not None and painting_data.year != painting.year
        )
        
        if need_new_unique_title:
            new_title = painting_data.title if painting_data.title is not None else painting.title
            new_year = painting_data.year if painting_data.year is not None else painting.year
            
            unique_title = _generate_painting_unique_title(
                title=new_title,
                year=new_year,
                db=db,
                exclude_id=painting_id
            )
            painting.unique_title = unique_title
        
        update_data = painting_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(painting, field, value)
        
        db.commit()
        db.refresh(painting)
        return painting
        
    except HTTPException as e: 
        logger.warning(f"HTTPException при обновлении картины: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Ошибка при обновлении картины: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при обновлении картины")
    
@router.delete(
        "/paintings/{painting_id}",
        summary="Удалить картину",
        description="Удаляет картину из системы по её ID"
)
@log_execution("delete_painting")
async def delete_painting(
    painting_id: int, 
    db: Session = Depends(get_db)
):
    """
    Удалить картину из системы.

    Параметры:
    - **painting_id**: ID удаляемой картины

    Возвращает:
    - Сообщение об успешном удалении и ID удаленной картины

    Исключения:
    - 404: Если картина с указанным ID не найдена
    - 500: При ошибке удаления из базы данных
    """
    try:
        painting = db.query(models.Painting).filter(models.Painting.id == painting_id).first()
        if not painting:
            raise HTTPException(
                status_code=404, 
                detail=f"Картина с ID {painting_id} не найдена"
            )
        
        db.delete(painting)
        db.commit()
        
        return {
            "message": f"Картина '{painting.title}' успешно удалена",
            "deleted_id": painting_id
        }
        
    except HTTPException as e:
        logger.warning(f"HTTPException при удалении картины: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Ошибка при удалении картины: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail="Ошибка при удалении картины"
        )

def _check_artist_exists(artist_id: int, db: Session) -> bool:
    artist = db.query(models.Artist).filter(models.Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Художник не найден")
    return True

def _check_museum_exists(museum_id: int, db: Session) -> bool:
    museum = db.query(models.Museum).filter(models.Museum.id == museum_id).first()
    if not museum:
        raise HTTPException(status_code=404, detail="Музей не найден")
    return True

def _generate_painting_unique_title(
    title: str, 
    year: Optional[int] = None, 
    db: Session = None, 
    exclude_id: Optional[int] = None
) -> str:
    try:
        base_title = transliterate.translit(title, 'ru', reversed=True).lower()
    except:
        base_title = title.lower()
    
    symbols_to_replace = [' ', '-', ',', ':', ';', '—', '–']
    
    for symbol in symbols_to_replace:
        base_title = base_title.replace(symbol, '_')
    
    clean_title = re.sub(r'[^a-zа-яё0-9_]', '', base_title)
    
    if year:
        unique_title_base = f"{clean_title}_{year}"
    else:
        unique_title_base = clean_title
    
    unique_title = unique_title_base
    counter = 1

    if db is None:
        return unique_title
    
    while True:
        query = db.query(models.Painting).filter(models.Painting.unique_title == unique_title)
        if exclude_id:
            query = query.filter(models.Painting.id != exclude_id)
        
        if not query.first():
            break
        
        unique_title = f"{unique_title_base}_{counter}"
        counter += 1
        
        if counter > 100:
            raise Exception("Слишком много попыток генерации unique_title")
    
    return unique_title
        
