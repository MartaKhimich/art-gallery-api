import pytest
from fastapi import status

class TestRootEndpoint:
    def test_root_endpoint(self, client):
        """Тест главной страницы"""
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Добро пожаловать в Art Gallery API!"}