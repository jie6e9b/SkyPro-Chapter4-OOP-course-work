class Vacancy:
    def __init__(self, title, url, salary_from=None, salary_to=None,
                 currency=None, description="", requirements="", **kwargs):
        """Инициализация объекта класса вакансия.
        Args:
            title (str): Название вакансии.
            url (str): Ссылка на источник вакансии.
            salary_from (int или None, optional): Нижняя граница зарплаты.
            salary_to (int или None, optional): Верхняя граница зарплаты.
            currency (str или None, optional): Валюта зарплаты.
            description (str, optional): Описание вакансии.
            requirements (str, optional): Требования к кандидату.
            **kwargs: Дополнительные параметры.
        """
        self.title = self._validate_title(title)
        self.url = self._validate_url(url)
        self.salary_from = self._validate_salary(salary_from)
        self.salary_to = self._validate_salary(salary_to)
        self.currency = currency or "RUB"
        self.description = description or "Описание не указано"
        self.requirements = requirements or "Требования не указаны"

    def _validate_title(self, title):
        """Валидация названия вакансии"""
        if not title or not isinstance(title, str):
            return "Название не указано"
        return title.strip()

    def _validate_url(self, url):
        """Валидация URL вакансии"""
        if not url or not isinstance(url, str):
            return ""
        return url.strip()

    def _validate_salary(self, salary):
        """Валидация зарплаты"""
        if salary is None or salary == "":
            return 0
        try:
            return int(float(salary))  # Обрабатывает int, float и строки
        except (ValueError, TypeError):
            return 0

    def __lt__(self, other):
        """Сравнение по зарплате для сортировки"""
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self.avg_salary < other.avg_salary

    @property
    def avg_salary(self):
        """Средняя зарплата для сравнения"""
        if self.salary_from > 0 and self.salary_to > 0:
            return (self.salary_from + self.salary_to) / 2
        elif self.salary_from > 0:
            return float(self.salary_from)
        elif self.salary_to > 0:
            return float(self.salary_to)
        return 0

    @classmethod
    def from_hh_dict(cls, data):
        """Создание объекта из словаря API HH"""
        if not isinstance(data, dict):
            raise ValueError("Данные должны быть словарем")

        salary = data.get('salary') or {}
        snippet = data.get('snippet') or {}

        return cls(
            title=data.get('name', ''),
            url=data.get('alternate_url', ''),
            salary_from=salary.get('from'),
            salary_to=salary.get('to'),
            currency=salary.get('currency'),
            description=snippet.get('responsibility', ''),
            requirements=snippet.get('requirement', '')
        )

    def to_dict(self):
        """Преобразование в словарь для сохранения"""
        return {
            'title': self.title,
            'url': self.url,
            'salary_from': self.salary_from,
            'salary_to': self.salary_to,
            'currency': self.currency,
            'description': self.description,
            'requirements': self.requirements
        }

    def __str__(self):
        """Красивое отображение вакансии"""
        salary_str = f"{self.salary_from}-{self.salary_to} {self.currency}" if self.salary_from or self.salary_to else "Зарплата не указана"
        return f"{self.title} | {salary_str}"

    def __repr__(self):
        """Техническое представление объекта"""
        return f"Vacancy(title='{self.title}', salary_from={self.salary_from}, salary_to={self.salary_to})"
