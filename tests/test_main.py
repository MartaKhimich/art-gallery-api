import pytest
from fastapi import status

class TestRootEndpoint:
    def test_root_endpoint(self, client):
        """Тест главной страницы"""
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Добро пожаловать в Art Gallery API!"}

class TestPaintingsEndpoints:
    def test_get_all_paintings_empty(self, client):
        """Тест получения картин когда БД пустая"""
        response = client.get("/paintings")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["has_next"] == False

    def test_get_all_paintings_with_data(self, client, sample_data):
        """Тест получения картин с данными"""
        response = client.get("/paintings")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["total"] == 1
        assert data["data"][0]["title"] == "Тестовая Картина"

    def test_get_all_paintings_pagination(self, client, sample_data):
        """Тест пагинации"""
        response = client.get("/paintings?page=2&page_size=1")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["page"] == 2
        assert data["has_prev"] == True

    def test_get_all_paintings_filter_by_artist(self, client, sample_data):
        """Тест фильтрации по художнику"""
        response = client.get("/paintings?artist_name=Тестовый")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["title"] == "Тестовая Картина"

    def test_get_all_paintings_sort_order(self, client, sample_data):
        """Тест сортировки"""
        response = client.get("/paintings?sort_order=desc")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1

    def test_get_painting_by_id_success(self, client, sample_data):
        """Тест успешного получения картины по ID"""
        painting_id = sample_data["painting"].id
        response = client.get(f"/paintings/{painting_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Тестовая Картина"
        assert data["id"] == painting_id

    def test_get_painting_by_id_not_found(self, client):
        """Тест получения несуществующей картины"""
        response = client.get("/paintings/999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "не найдена" in response.json()["detail"]

    def test_get_painting_by_id_invalid_id(self, client):
        """Тест с некорректным ID"""
        response = client.get("/paintings/not_a_number")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY        