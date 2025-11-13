import pytest
from app.models import Artist, Museum, Painting
from sqlalchemy.exc import IntegrityError

class TestDatabaseModels:
    def test_artist_required_fields(self, test_db):
        """Тест обязательных полей художника"""
        artist = Artist(
            # Пропущены обязательные поля
            artist_long_name="Только это поле"
        )
        test_db.add(artist)
        
        with pytest.raises(Exception): 
            test_db.commit()

    def test_museum_unique_constraint(self, test_db):
        """Тест уникальности name_unique для музеев"""
        museum1 = Museum(
            name="Музей 1",
            name_unique="unique_museum", 
            city="Москва",
            country="Россия"
        )
        test_db.add(museum1)
        test_db.commit()
    
        museum2 = Museum(
            name="Музей 2", 
            name_unique="unique_museum",  # Дубликат
            city="СПб",
            country="Россия"
        )
        test_db.add(museum2)
    
        with pytest.raises(IntegrityError):
            test_db.commit()
        test_db.rollback()

    def test_painting_relationships(self, test_db, sample_data):
        """Тест связей картины с художником и музеем"""
        painting = test_db.query(Painting).first()
        
        assert painting.artist is not None
        assert painting.museum is not None
        assert painting.artist_id == sample_data["artist"].id
        assert painting.museum_id == sample_data["museum"].id

    def test_auto_timestamps(self, test_db, sample_data):
        """Тест автоматических временных меток"""
        painting = sample_data["painting"]
        
        assert painting.created_at is not None
        # updated_at будет None пока нет обновлений
        assert painting.updated_at is None
        
        # Обновляем и проверяем updated_at
        painting.title = "Обновленное название"
        test_db.commit()
        test_db.refresh(painting)
        
        assert painting.updated_at is not None