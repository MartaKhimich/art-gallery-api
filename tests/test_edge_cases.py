import pytest
from fastapi import status

class TestPaintingsEdgeCases:
    def test_get_painting_by_id_not_found(self, client):
        """Тест получения несуществующей картины"""
        response = client.get("/paintings/999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "не найдена" in response.json()["detail"]

    def test_get_painting_by_id_invalid_id(self, client):
        """Тест с некорректным ID"""
        response = client.get("/paintings/not_a_number")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY   
