import pytest
from fastapi import status
import time

class TestBusinessLogic:
    def test_unique_title_regeneration_on_title_change(self, client, sample_painting):
        """Тест что unique_title перегенерируется при изменении названия"""
        
        get_response = client.get(f"/paintings/{sample_painting.id}")
        original_unique_title = get_response.json()["unique_title"]

        response = client.put(f"/paintings/{sample_painting.id}", json={
            "title": "Совершенно Новое Название"
        })
        
        assert response.status_code == status.HTTP_200_OK
        new_unique_title = response.json()["unique_title"]
        
        # Проверка что unique_title изменился
        assert original_unique_title != new_unique_title
        assert "sovershenno_novoe_nazvanie" in new_unique_title
    
    def test_unique_title_regeneration_on_year_change(self, client, sample_painting):
        """Тест что unique_title перегенерируется при изменении года"""
        
        get_response = client.get(f"/paintings/{sample_painting.id}")
        original_unique_title = get_response.json()["unique_title"]
        
        response = client.put(f"/paintings/{sample_painting.id}", json={
            "year": 2000
        })
        
        assert response.status_code == status.HTTP_200_OK
        new_unique_title = response.json()["unique_title"]
        
        # Проверка что unique_title изменился и содержит новый год
        assert original_unique_title != new_unique_title
        assert "2000" in new_unique_title
    
    def test_duplicate_unique_title_handling(self, client, sample_artist, sample_museum):
        """Тест обработки дубликатов unique_title"""
        
        data1 = {
            "title": "Уникальная Картина", 
            "year": 2024,
            "artist_id": sample_artist.id,
            "museum_id": sample_museum.id
        }
        response1 = client.post("/paintings", json=data1)
        assert response1.status_code == status.HTTP_201_CREATED
        first_unique_title = response1.json()["unique_title"]
        
        data2 = {
            "title": "Уникальная Картина",  # То же название
            "year": 2024,                   # Тот же год
            "artist_id": sample_artist.id,
            "museum_id": sample_museum.id
        }
        response2 = client.post("/paintings", json=data2)
        assert response2.status_code == status.HTTP_201_CREATED
        second_unique_title = response2.json()["unique_title"]
        
        assert first_unique_title != second_unique_title
        
        assert second_unique_title == f"{first_unique_title}_1"