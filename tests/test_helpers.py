import pytest
from fastapi import HTTPException
from unittest.mock import Mock
from app.routers.paintings import _generate_painting_unique_title, _check_artist_exists, _check_museum_exists

class TestHelperFunctions:
    def test_generate_unique_title_basic(self):
        """Тест базовой генерации unique_title"""
        result = _generate_painting_unique_title("Тест Картина", 2024, None, None)
        assert result == "test_kartina_2024"
    
    def test_generate_unique_title_with_special_chars(self):
        """Тест генерации с специальными символами"""
        result = _generate_painting_unique_title("Картина #1!", 2024, None, None)
        assert result == "kartina_1_2024"
    
    def test_generate_unique_title_without_year(self):
        """Тест генерации без года"""
        result = _generate_painting_unique_title("Тест", None, None, None)
        assert result == "test"
    
    def test_generate_unique_title_unique_check(self):
        """Тест проверки уникальности с базой данных"""
        mock_db = Mock()
        mock_painting = Mock()
        
        # Настройка mock чтобы первый вызов возвращал картину (уже существует), второй - None (уникально)
        mock_db.query.return_value.filter.return_value.first.side_effect = [mock_painting, None]
        
        result = _generate_painting_unique_title("Тест", 2024, mock_db, None)
        assert result == "test_2024_1"  # Должен добавить номер
    
    def test_check_artist_exists_success(self):
        """Тест успешной проверки художника"""
        mock_db = Mock()
        mock_artist = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_artist
        
        result = _check_artist_exists(1, mock_db)
        assert result is True
    
    def test_check_artist_exists_not_found(self):
        """Тест проверки несуществующего художника"""
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            _check_artist_exists(999, mock_db)
        assert exc_info.value.status_code == 404