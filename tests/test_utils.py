import pytest
from unittest.mock import MagicMock
from src.utils import UserInterface
from src.vacancy import Vacancy


@pytest.fixture
def ui():
    """Создаёт объект UserInterface с подменёнными API и хранилищем"""
    ui = UserInterface()
    ui.api = MagicMock()
    ui.storage = MagicMock()
    return ui


@pytest.fixture
def sample_vacancies():
    return [
        Vacancy(title="Python Dev", url="http://test/1", salary_from=100000, salary_to=150000),
        Vacancy(title="QA Engineer", url="http://test/2", salary_from=80000, salary_to=120000),
    ]


def test_get_int_input_with_valid(monkeypatch, ui):
    monkeypatch.setattr("builtins.input", lambda _: "10")
    result = ui._get_int_input("Введите число", min_val=5, max_val=20)
    assert result == 10


def test_get_int_input_with_default(monkeypatch, ui):
    monkeypatch.setattr("builtins.input", lambda _: "")
    result = ui._get_int_input("Введите число", default=3)
    assert result == 3


def test_format_salary_range(ui):
    v = Vacancy("Test", "url", salary_from=100000, salary_to=150000, currency="RUB")
    assert ui._format_salary(v) == "100000 - 150000 RUB"


def test_format_salary_only_from(ui):
    v = Vacancy("Test", "url", salary_from=90000, salary_to=None, currency="RUB")
    assert ui._format_salary(v) == "от 90000 RUB"


def test_format_salary_none(ui):
    v = Vacancy("Test", "url", salary_from=None, salary_to=None, currency="RUB")
    assert ui._format_salary(v) == "Не указана"


def test_display_vacancies(capsys, ui, sample_vacancies):
    ui._display_vacancies(sample_vacancies)
    captured = capsys.readouterr()
    assert "Python Dev" in captured.out
    assert "QA Engineer" in captured.out


def test_get_search_keyword_valid(monkeypatch, ui):
    monkeypatch.setattr("builtins.input", lambda _: "Backend Developer")
    assert ui._get_search_keyword() == "Backend Developer"


def test_show_saved_vacancies_with_data(capsys, ui, sample_vacancies):
    ui.storage.get_vacancies.return_value = sample_vacancies
    ui._show_saved_vacancies()
    captured = capsys.readouterr()
    assert "Всего сохранено 2 вакансий" in captured.out


def test_show_saved_vacancies_empty(capsys, ui):
    ui.storage.get_vacancies.return_value = []
    ui._show_saved_vacancies()
    captured = capsys.readouterr()
    assert "Сохраненных вакансий нет" in captured.out


def test_show_top_vacancies_valid_input(monkeypatch, capsys, ui, sample_vacancies):
    monkeypatch.setattr("builtins.input", lambda _: "1")
    ui.storage.get_vacancies.return_value = sample_vacancies
    ui._show_top_vacancies()
    captured = capsys.readouterr()
    assert "Топ 1 вакансий по зарплате" in captured.out


def test_show_top_vacancies_invalid_input(monkeypatch, capsys, ui):
    monkeypatch.setattr("builtins.input", lambda _: "abc")
    ui._show_top_vacancies()
    captured = capsys.readouterr()
    assert "Введите корректное число" in captured.out


def test_search_by_keyword_found(monkeypatch, capsys, ui, sample_vacancies):
    monkeypatch.setattr("builtins.input", lambda _: "Python")
    ui.storage.get_vacancies.return_value = [sample_vacancies[0]]
    ui._search_by_keyword()
    captured = capsys.readouterr()
    assert "Найдено 1 вакансий с ключевым словом" in captured.out


def test_search_by_keyword_not_found(monkeypatch, capsys, ui):
    monkeypatch.setattr("builtins.input", lambda _: "NoMatch")
    ui.storage.get_vacancies.return_value = []
    ui._search_by_keyword()
    captured = capsys.readouterr()
    assert "не найдено" in captured.out


def test_clear_vacancies_confirm(monkeypatch, capsys, ui):
    monkeypatch.setattr("builtins.input", lambda _: "да")
    ui._clear_vacancies()
    captured = capsys.readouterr()
    assert "Все вакансии удалены" in captured.out
    ui.storage.clear_storage.assert_called_once()


def test_clear_vacancies_cancel(monkeypatch, capsys, ui):
    monkeypatch.setattr("builtins.input", lambda _: "нет")
    ui._clear_vacancies()
    captured = capsys.readouterr()
    assert "Все вакансии удалены" not in captured.out
    ui.storage.clear_storage.assert_not_called()
