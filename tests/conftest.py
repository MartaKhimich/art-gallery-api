import pytest
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
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
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
def sample_data(test_db):
    from app.models import Artist, Museum, Painting
    
    artist = Artist(
        artist_short_name="Тестовый Художник",
        artist_long_name="Тестовый Художник Полное Имя",
        dob="1900-01-01",
        dob_place="Москва",
        dod="2000-01-01", 
        dod_place="Москва"
    )
    test_db.add(artist)
    
    museum = Museum(
        name="Тестовый Музей",
        name_unique="test_museum",
        city="Москва",
        country="Россия",
        country_code=7
    )
    test_db.add(museum)
    
    test_db.commit()
    test_db.refresh(artist)
    test_db.refresh(museum)
    
    painting = Painting(
        title="Тестовая Картина",
        unique_title="test_painting",
        type="живопись",
        genre="Пейзаж",
        materials=["холст", "масло"],
        size="50 на 70",
        year=1950,
        period="Современное искусство",
        style=["реализм"],
        artist_id=artist.id,
        museum_id=museum.id
    )
    test_db.add(painting)
    test_db.commit()
    test_db.refresh(painting)
    
    return {
        "artist": artist,
        "museum": museum, 
        "painting": painting
    }