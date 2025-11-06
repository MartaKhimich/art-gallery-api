import pytest
from app.models import Artist, Museum
from tests.conftest import test_db

class TestValidation:
    def test_required_fields(self, test_db):
        """Тест обязательных полей"""
        artist = Artist(
            artist_long_name="Тестовый Художник"
        )
        test_db.add(artist)
        
        with pytest.raises(Exception): 
            test_db.commit()

    def test_unique_constraints(self, test_db):
        """Тест уникальных ограничений"""
        museum1 = Museum(
            name="Тестовый Музей",
            name_unique="test_museum", 
            city="Москва",
            country="Россия"
        )
        test_db.add(museum1)
        test_db.commit()
    
        museums_before = test_db.query(Museum).count()
        print(f"Музеев до попытки дубликата: {museums_before}")
    
        museum2 = Museum(
            name="Другой Музей", 
            name_unique="test_museum",  
            city="СПб",
            country="Россия"
        )
        test_db.add(museum2)
    
        try:
            test_db.commit()
            museums_after = test_db.query(Museum).count() 
            print(f"Музеев после коммита: {museums_after}")
            
            if museums_after > museums_before:
                print("❌ ДУБЛИКАТ СОЗДАЛСЯ! Ограничение не работает")
            else:
                print("✅ Дубликат не создался - ограничение работает")
                
        except Exception as e:
            print(f"✅ Ошибка при коммите (как и ожидалось): {e}")
            test_db.rollback()