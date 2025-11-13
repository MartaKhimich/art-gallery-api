import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db
from app.models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def test_db():
    """Фикстура для тестовой базы данных"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
    """Фикстура для тестового клиента FastAPI"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_artist(test_db):
    """Фикстура для тестового художника"""
    from app.models import Artist
    
    artist = Artist(
        artist_short_name="Тестовый Художник",
        artist_long_name="Тестовый Художник Полное Имя",
        dob="1900-01-01",
        dob_place="Москва",
        dod="2000-01-01", 
        dod_place="Москва"
    )
    test_db.add(artist)
    test_db.commit()
    test_db.refresh(artist)
    return artist

@pytest.fixture
def sample_museum(test_db):
    """Фикстура для тестового музея"""
    from app.models import Museum
    
    unique_suffix = str(uuid.uuid4())[:8]
    
    museum = Museum(
        name="Тестовый Музей",
        name_unique=f"test_museum_{unique_suffix}",
        city="Москва",
        country="Россия",
        country_code=7
    )
    test_db.add(museum)
    test_db.commit()
    test_db.refresh(museum)
    return museum

@pytest.fixture
def sample_painting(test_db, sample_artist, sample_museum):
    """Фикстура для тестовой картины"""
    from app.models import Painting
    
    unique_suffix = str(uuid.uuid4())[:8]

    painting = Painting(
        title="Тестовая Картина",
        unique_title=f"test_painting_1950_{unique_suffix}", 
        type="живопись",
        genre="Пейзаж",
        materials=["холст", "масло"],
        size="50 на 70",
        year=1950,
        period="Современное искусство",
        style=["реализм"],
        artist_id=sample_artist.id,
        museum_id=sample_museum.id
    )
    test_db.add(painting)
    test_db.commit()
    test_db.refresh(painting)
    return painting

@pytest.fixture
def sample_data(sample_artist, sample_museum, sample_painting):
    """Общая фикстура со всеми тестовыми данными"""
    return {
        "artist": sample_artist,
        "museum": sample_museum, 
        "painting": sample_painting
    }