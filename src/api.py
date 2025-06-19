from abc import ABC, abstractmethod
import requests
from typing import List, Dict, Any, Optional
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ParserError(Exception):
    """Базовое исключение для парсеров"""
    pass


class ConnectionError(ParserError):
    """Ошибка подключения к API"""
    pass


class Parser(ABC):
    """Абстрактный базовый класс для парсеров вакансий"""

    @abstractmethod
    def connect(self) -> bool:
        """ Метод подключения к API
        Returns: bool: True если подключение успешно
        Raises: ConnectionError: При ошибке подключения """
        pass

    @abstractmethod
    def load_vacancies(self, keyword: str, **kwargs) -> List[Dict[str, Any]]:
        """ Метод получения вакансий
        Args: keyword: Ключевое слово для поиска
              **kwargs: Дополнительные параметры поиска
        Returns: List[Dict[str, Any]]: Список вакансий
        Raises: ParserError: При ошибке получения данных """
        pass


class HH(Parser):
    """Класс для работы с API HeadHunter"""

    BASE_URL = "https://api.hh.ru"
    VACANCIES_ENDPOINT = "/vacancies"
    DEFAULT_PER_PAGE = 100
    MAX_PAGES = 20  # HH API ограничение

    def __init__(self, timeout: int = 10, max_retries: int = 3):
        """ Инициализация парсера HH
        Args: timeout: Таймаут запросов в секундах
              max_retries: Максимальное количество повторных попыток"""
        self._session: Optional[requests.Session] = None
        self._url = f"{self.BASE_URL}{self.VACANCIES_ENDPOINT}"
        self._headers = {"User-Agent": "VacancyParser"}
        self._timeout = timeout
        self._max_retries = max_retries
        self._setup_session()

    def _setup_session(self) -> None:
        """Настройка сессии с retry стратегией"""
        self._session = requests.Session()
        # Настройка retry стратегии
        retry_strategy = Retry(
            total=self._max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)
        self._session.headers.update(self._headers)

    def connect(self) -> bool:
        """ Проверка подключения к API HeadHunter
        Returns: bool: True если подключение успешно
        Raises: ConnectionError: При ошибке подключения """

        try:
            response = self._session.get(
                self._url,
                params={"per_page": 1},
                timeout=self._timeout
            )
            response.raise_for_status()
            logger.info("Успешное подключение к API HeadHunter")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка подключения к API HeadHunter: {e}")
            raise ConnectionError(f"Не удалось подключиться к API: {e}")

    def load_vacancies(
            self,
            keyword: str,
            max_pages: Optional[int] = None,
            per_page: int = DEFAULT_PER_PAGE,
            area: Optional[int] = None,
            salary_from: Optional[int] = None,
            salary_to: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """ Загрузка вакансий с HeadHunter
        Args: keyword: Ключевое слово для поиска
              max_pages: Максимальное количество страниц (по умолчанию 2)
              per_page: Количество вакансий на странице
              area: ID региона
              salary_from: Минимальная зарплата
              salary_to: Максимальная зарплата

        Returns: List[Dict[str, Any]]: Список вакансий
        Raises: ParserError: При ошибке получения данных"""

        if not keyword.strip():
            raise ValueError("Ключевое слово не может быть пустым")

        if max_pages is None:
            max_pages = 2

        max_pages = min(max_pages, self.MAX_PAGES)

        # Проверяем подключение
        self.connect()

        params = {
            "text": keyword.strip(),
            "per_page": min(per_page, self.DEFAULT_PER_PAGE),
            "page": 0
        }

        # Добавляем дополнительные параметры если они указаны
        if area is not None:
            params["area"] = 113
        if salary_from is not None:
            params["salary"] = 0
        if salary_to is not None:
            params["salary"] = 500000

        vacancies = []

        try:
            for page in range(max_pages):
                params["page"] = page
                logger.info(f"Загрузка страницы {page + 1} из {max_pages}")

                response = self._session.get(
                    self._url,
                    params=params,
                    timeout=self._timeout
                )
                response.raise_for_status()

                data = response.json()
                items = data.get("items", [])

                if not items:
                    logger.info("Больше вакансий не найдено")
                    break

                vacancies.extend(items)

                # Проверяем, есть ли еще страницы
                if page >= data.get("pages", 0) - 1:
                    break

            logger.info(f"Загружено {len(vacancies)} вакансий по запросу '{keyword}'")
            return vacancies

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при загрузке вакансий: {e}")
            raise ParserError(f"Ошибка при получении данных: {e}")

    def __enter__(self):
        """Поддержка контекстного менеджера"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Закрытие сессии при выходе из контекста"""
        if self._session:
            self._session.close()

