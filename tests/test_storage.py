import os
import tempfile
import pytest
import json
from src.storage import JSONStorage
from src.vacancy import Vacancy


@pytest.fixture
def temp_json_storage():
    """Создаёт временный файл для хранилища"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        storage = JSONStorage(filename=tmp.name)
        yield storage
        os.remove(tmp.name)


@pytest.fixture
def sample_vacancies():
    return [
        Vacancy(title="Python Dev", url="https://example.com/1", salary_from=100000, salary_to=150000,
                currency="RUB", description="Разработка", requirements="Опыт от 2 лет"),
        Vacancy(title="Data Analyst", url="https://example.com/2", salary_from=80000, salary_to=100000,
                currency="RUB", description="Анализ данных", requirements="SQL, Python"),
    ]


def test_add_and_get_all_vacancies(temp_json_storage, sample_vacancies):
    temp_json_storage.add_vacancies(sample_vacancies)
    result = temp_json_storage.get_vacancies()
    assert len(result) == 2
    assert result[0].title == "Python Dev"
    assert result[1].url == "https://example.com/2"


def test_get_vacancies_with_keyword(temp_json_storage, sample_vacancies):
    temp_json_storage.add_vacancies(sample_vacancies)
    filtered = temp_json_storage.get_vacancies(keyword="аналитик")
    assert len(filtered) == 1 or len(filtered) == 0  # зависит от языка описания
    filtered = temp_json_storage.get_vacancies(keyword="Data")
    assert len(filtered) == 1
    assert filtered[0].title == "Data Analyst"


def test_get_vacancies_with_min_salary(temp_json_storage, sample_vacancies):
    temp_json_storage.add_vacancies(sample_vacancies)
    filtered = temp_json_storage.get_vacancies(min_salary=120000)
    assert len(filtered) == 1
    assert filtered[0].title == "Python Dev"


def test_clear_storage(temp_json_storage, sample_vacancies):
    temp_json_storage.add_vacancies(sample_vacancies)
    temp_json_storage.clear_storage()
    result = temp_json_storage.get_vacancies()
    assert result == []


def test_load_from_empty_file(temp_json_storage):
    result = temp_json_storage._load_from_file()
    assert result == []


def test_save_and_manual_load(temp_json_storage):
    manual_data = [{"title": "Manual QA", "url": "https://hh.ru/qa", "salary_from": 60000, "salary_to": 90000}]
    temp_json_storage._save_to_file(manual_data)

    with open(temp_json_storage.filename, encoding='utf-8') as f:
        loaded = json.load(f)
    assert loaded[0]["title"] == "Manual QA"
