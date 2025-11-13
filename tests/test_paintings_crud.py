import pytest
from fastapi import status
from app.models import Artist, Museum
from app.dependencies import get_db

class TestPaintingsCRUD:
    # ТЕСТЫ СОЗДАНИЯ (POST)
    def test_create_painting_success(self, client, sample_artist, sample_museum):
        """Тест успешного создания картины"""
        data = {
            "title": "Новая Картина",
            "type": "живопись", 
            "year": 2024,
            "artist_id": sample_artist.id,
            "museum_id": sample_museum.id
        }
        response = client.post("/paintings", json=data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["title"] == "Новая Картина"
        assert "unique_title" in response.json()
    
    def test_create_painting_auto_generate_unique_title(self, client, sample_artist, sample_museum):
        """Тест автоматической генерации unique_title"""
        data = {
            "title": "Тестовая Картина",
            "year": 2024,
            "artist_id": sample_artist.id,
            "museum_id": sample_museum.id
        }
        response = client.post("/paintings", json=data)
        assert response.status_code == status.HTTP_201_CREATED
        # Проверяем что unique_title сгенерирован автоматически
        assert "testovaja_kartina_2024" in response.json()["unique_title"]
    
    def test_create_painting_missing_required_fields(self, client):
        """Тест создания без обязательных полей"""
        data = {
            "title": "Картина"
            # Нет artist_id и museum_id
        }
        response = client.post("/paintings", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_painting_nonexistent_artist(self, client, sample_museum):
        """Тест создания с несуществующим художником"""
        data = {
            "title": "Картина",
            "artist_id": 999,  # несуществующий ID
            "museum_id": sample_museum.id
        }
        response = client.post("/paintings", json=data)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Художник не найден" in response.json()["detail"]
    
    def test_create_painting_nonexistent_museum(self, client, sample_artist):
        """Тест создания с несуществующим музеем"""
        data = {
            "title": "Картина",
            "artist_id": sample_artist.id,
            "museum_id": 999  # несуществующий ID
        }
        response = client.post("/paintings", json=data)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Музей не найден" in response.json()["detail"]

    # ТЕСТЫ ОБНОВЛЕНИЯ (PUT)
    def test_update_painting_success(self, client, sample_painting):
        """Тест успешного обновления"""
        data = {"title": "Обновленное Название"}
        response = client.put(f"/paintings/{sample_painting.id}", json=data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["title"] == "Обновленное Название"
    
    def test_update_painting_change_year_regenerates_unique_title(self, client, sample_painting):
        """Тест что смена года перегенерирует unique_title"""
        original_unique_title = sample_painting.unique_title
        
        data = {"year": 2025}
        response = client.put(f"/paintings/{sample_painting.id}", json=data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["year"] == 2025
        # unique_title должен измениться
        assert response.json()["unique_title"] != original_unique_title
        assert "2025" in response.json()["unique_title"]
    
    def test_update_painting_nonexistent_id(self, client):
        """Тест обновления несуществующей картины"""
        data = {"title": "Новое название"}
        response = client.put("/paintings/999", json=data)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_painting_change_artist(self, client, sample_painting, sample_artist):
        """Тест смены художника"""
        
        db = next(client.app.dependency_overrides[get_db]())
        new_artist = Artist(
            artist_short_name="Другой Художник",
            artist_long_name="Другой Художник Полное Имя"
        )
        db.add(new_artist)
        db.commit()
        db.refresh(new_artist)
        
        data = {"artist_id": new_artist.id}
        response = client.put(f"/paintings/{sample_painting.id}", json=data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["artist"]["id"] == new_artist.id
        assert response.json()["artist"]["artist_short_name"] == "Другой Художник"
    
    def test_update_painting_invalid_data(self, client, sample_painting):
        """Тест обновления с некорректными данными"""
        data = {"year": "не число"}  # год должен быть числом
        response = client.put(f"/paintings/{sample_painting.id}", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # ТЕСТЫ УДАЛЕНИЯ (DELETE)
    def test_delete_painting_success(self, client, sample_painting):
        """Тест успешного удаления"""
        response = client.delete(f"/paintings/{sample_painting.id}")
        assert response.status_code == status.HTTP_200_OK
        assert "успешно удалена" in response.json()["message"]
        
        # Проверяем что картина действительно удалена
        get_response = client.get(f"/paintings/{sample_painting.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_painting_nonexistent_id(self, client):
        """Тест удаления несуществующей картины"""
        response = client.delete("/paintings/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_painting_and_verify_relationships(self, client, sample_data):
        """Тест что удаление картины не затрагивает художника и музей"""
        painting_id = sample_data["painting"].id
        artist_id = sample_data["artist"].id
        museum_id = sample_data["museum"].id
        
        # Удаляем картину
        response = client.delete(f"/paintings/{painting_id}")
        assert response.status_code == status.HTTP_200_OK
        
        # Проверяем что художник и музей остались
        db = next(client.app.dependency_overrides[get_db]())
        artist = db.query(Artist).filter(Artist.id == artist_id).first()
        museum = db.query(Museum).filter(Museum.id == museum_id).first()
        
        assert artist is not None
        assert museum is not None