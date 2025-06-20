import pytest
import requests
from unittest.mock import patch, MagicMock
from src.api import HH, ConnectionError, ParserError


@pytest.fixture
def hh_instance():
    """Фикстура: возвращает экземпляр HH с таймаутом и ретраями"""
    return HH(timeout=1, max_retries=1)


def test_connect_success(hh_instance):
    """Тест успешного подключения к API"""
    with patch.object(hh_instance._session, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        assert hh_instance.connect() is True
        mock_get.assert_called_once()


def test_connect_failure(hh_instance):
    """Тест ошибки подключения к API"""
    with patch.object(hh_instance._session, 'get',
                      side_effect=requests.exceptions.RequestException("Connection failed")):
        with pytest.raises(ConnectionError):
            hh_instance.connect()


def test_load_vacancies_empty_keyword(hh_instance):
    """Тест загрузки вакансий с пустым ключевым словом"""
    with pytest.raises(ValueError):
        hh_instance.load_vacancies("  ")


def test_load_vacancies_success(hh_instance):
    """Тест успешной загрузки вакансий"""
    sample_data = {
        "items": [{"id": "1", "name": "Python Developer"}],
        "pages": 1
    }

    with patch.object(hh_instance, 'connect', return_value=True), \
            patch.object(hh_instance._session, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = sample_data
        mock_get.return_value = mock_response

        result = hh_instance.load_vacancies("Python")
        assert isinstance(result, list)
        assert result[0]["name"] == "Python Developer"


def test_load_vacancies_no_items(hh_instance):
    """Тест случая, когда API возвращает пустой список"""
    sample_data = {
        "items": [],
        "pages": 1
    }

    with patch.object(hh_instance, 'connect', return_value=True), \
            patch.object(hh_instance._session, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = sample_data
        mock_get.return_value = mock_response

        result = hh_instance.load_vacancies("Python")
        assert result == []


def test_load_vacancies_api_failure(hh_instance):
    """Тест ошибки во время запроса к API"""
    with patch.object(hh_instance, 'connect', return_value=True), \
            patch.object(hh_instance._session, 'get', side_effect=requests.exceptions.RequestException("API failed")):
        with pytest.raises(ParserError):
            hh_instance.load_vacancies("Python")
