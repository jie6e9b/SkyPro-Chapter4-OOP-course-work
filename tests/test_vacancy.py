import pytest
from src.vacancy import Vacancy


def test_vacancy_initialization():
    v = Vacancy("Python Dev", "https://hh.ru/vac1", 100000, 150000, "RUB", "desc", "req")
    assert v.title == "Python Dev"
    assert v.url == "https://hh.ru/vac1"
    assert v.salary_from == 100000
    assert v.salary_to == 150000
    assert v.currency == "RUB"
    assert v.description == "desc"
    assert v.requirements == "req"


@pytest.mark.parametrize("title,expected", [
    ("", "Название не указано"),
    (None, "Название не указано"),
    ("  Java Dev ", "Java Dev"),
])
def test_validate_title(title, expected):
    v = Vacancy(title, "url")
    assert v.title == expected


@pytest.mark.parametrize("url,expected", [
    ("", ""),
    (None, ""),
    (" https://hh.ru/test ", "https://hh.ru/test"),
])
def test_validate_url(url, expected):
    v = Vacancy("Title", url)
    assert v.url == expected


@pytest.mark.parametrize("salary_input,expected", [
    (None, 0),
    ("", 0),
    ("100000", 100000),
    (150000.0, 150000),
    ("invalid", 0),
])
def test_validate_salary(salary_input, expected):
    v = Vacancy("Title", "url", salary_from=salary_input)
    assert v.salary_from == expected


@pytest.mark.parametrize("s_from,s_to,expected", [
    (100000, 200000, 150000.0),
    (50000, None, 50000.0),
    (None, 90000, 90000.0),
    (None, None, 0),
])
def test_avg_salary(s_from, s_to, expected):
    v = Vacancy("Test", "url", salary_from=s_from, salary_to=s_to)
    assert v.avg_salary == expected


def test_vacancy_comparison():
    v1 = Vacancy("Dev1", "url", salary_from=100000, salary_to=150000)
    v2 = Vacancy("Dev2", "url", salary_from=150000, salary_to=200000)
    assert v1 < v2
    assert not v2 < v1


def test_from_hh_dict_valid():
    data = {
        "name": "Python Dev",
        "alternate_url": "https://hh.ru/vac1",
        "salary": {"from": 100000, "to": 150000, "currency": "RUB"},
        "snippet": {"responsibility": "write code", "requirement": "know Python"}
    }
    v = Vacancy.from_hh_dict(data)
    assert isinstance(v, Vacancy)
    assert v.salary_from == 100000
    assert v.requirements == "know Python"


def test_from_hh_dict_invalid():
    with pytest.raises(ValueError):
        Vacancy.from_hh_dict("not a dict")


def test_to_dict():
    v = Vacancy("Python Dev", "url", 100000, 150000, "RUB", "desc", "req")
    d = v.to_dict()
    assert isinstance(d, dict)
    assert d["title"] == "Python Dev"
    assert d["salary_from"] == 100000


def test_str_and_repr():
    v = Vacancy("QA", "url", 50000, 100000, "RUB")
    assert str(v) == "QA | 50000-100000 RUB"
    assert "Vacancy(title='QA'" in repr(v)
