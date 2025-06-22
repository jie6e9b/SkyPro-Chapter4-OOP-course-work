import os
import json
from abc import ABC, abstractmethod
from enum import unique
from typing import List
from src.vacancy import Vacancy


class Storage(ABC):
    @abstractmethod
    def add_vacancies(self, vacancies: List[Vacancy]):
        """Добавить вакансии в хранилище"""
        pass

    @abstractmethod
    def get_vacancies(self, **criteria) -> List[Vacancy]:
        """Получить вакансии по критериям"""
        pass

    @abstractmethod
    def delete_vacancies(self, **criteria):
        """Удалить вакансии по критериям"""
        pass

    @abstractmethod
    def clear_storage(self):
        """Очистить хранилище"""
        pass


class JSONStorage(Storage):
    def __init__(self, filename: str = None):
        """ Инициализация хранилища JSON-файла.
            :param filename: Путь к JSON-файлу. По умолчанию используется src/vacancies.json"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.filename = filename or os.path.join(base_dir, "data", "vacancies.json")

    def add_vacancies(self, vacancies: List[Vacancy]):
        """Добавить вакансии в JSON файл"""
        existing = self._load_from_file()
        existing_set = {json.dump(item, sort_keys=True) for item in existing}
        new_data = [v.to_dict() for v in vacancies]
        unique_new_data = [item for item in new_data if json.dump(item, sort_keys=True) not in existing_set]
        existing.extend(unique_new_data)
        self._save_to_file(existing)

    def get_vacancies(self, **criteria) -> List[Vacancy]:
        """Получить вакансии с фильтрацией"""
        data = self._load_from_file()
        vacancies = [Vacancy(**item) for item in data]

        # Фильтрация
        if 'keyword' in criteria:
            keyword = criteria['keyword'].lower()
            vacancies = [v for v in vacancies if
                         keyword in v.title.lower() or
                         keyword in v.description.lower()]

        if 'min_salary' in criteria:
            min_sal = criteria['min_salary']
            vacancies = [v for v in vacancies if v.avg_salary >= min_sal]

        return vacancies

    def delete_vacancies(self, **criteria):
        """Удалить вакансии по критериям"""
        # Заглушка для будущей интеграции с БД
        pass

    def clear_storage(self):
        """Очистить файл"""
        self._save_to_file([])

    def _load_from_file(self) -> List[dict]:
        """Загрузить данные из файла"""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []

    def _save_to_file(self, data: List[dict]):
        """Сохранить данные в файл"""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
