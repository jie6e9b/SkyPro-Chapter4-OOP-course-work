from abc import ABC, abstractmethod
import requests
import logging
from typing import Optional, Dict, Any, List
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
            per_page: int = DEFAULT_PER_PAGE,
            max_pages: Optional[int] = None,
            area: Optional[int] = None,
            salary_from: Optional[int] = None,
            salary_to: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """ Загрузка вакансий с HeadHunter
        Args: keyword: Ключевое слово для поиска
              max_pages: Максимальное количество страниц (по умолчанию 2)
              per_page: Количество вакансий на странице (по умолчанию 100)
              area: ID региона (113 Россия,1 Москва)
              salary_from: Минимальная зарплата
              salary_to: Максимальная зарплата

        Returns: List[Dict[str, Any]]: Список вакансий
        Raises: ValueError: При пустом ключевом слове
                ConnectionError: Не удалось подключиться к API"""

        # Проверяем ключевое слово
        if not keyword.strip():
            raise ValueError("Ключевое слово не может быть пустым")

        # Определяем переменную максимальное количество страниц
        if max_pages is None:
            max_pages = 2
        max_pages = min(max_pages, self.MAX_PAGES)

        # Подготовка параметров для HTTP-запроса к API HeadHunter
        params = {
            "text": keyword.strip(),
            "per_page": min(per_page, self.DEFAULT_PER_PAGE),
            "page": 0
        }

        # Добавляем дополнительные параметры если они указаны
        if area is not None:
            params["area"] = area
        if salary_from is not None:
            params["salary"] = salary_from
        if salary_to is not None:
            # HeadHunter использует отдельные параметры для min и max зарплаты
            if salary_from and salary_to:
                # Если указаны обе границы, используем формат "от-до"
                params["salary_range"] = f"{salary_from}-{salary_to}"
            else:
                # Если только максимальная зарплата
                params["salary_range"] = f"0-{salary_to}"

        logger.info(f"Параметры HTTP - запроса к API HeadHunter - {params}")

        # Проверяем подключение
        self.connect()

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

                # Проверяем код HTTP ответа
                response.raise_for_status()

                # Преобразуем (парсим) JSON - строку из ответа в список словарей
                data = response.json()

                # Безопасно извлекаем список вакансий по ключу "items"
                # Если API вернет неожиданную структуру без "items",
                # получим пустой список вместо ошибки
                items = data.get("items", [])

                # Проверяем есть ли в ответе нет "items", если нет прерываем цикл
                if not items:
                    logger.info(f"Вакансий на странице {page + 1} не найдено")
                    break

                # Проверяем есть ли в ответе нет "items", если нет прерываем цикл
                vacancies.extend(items)
                logger.info(f"Загружено {len(items)} вакансий со страницы {page + 1}")

                # Проверяем, есть ли еще страницы
                total_pages = data.get("pages", 0)
                if page >= total_pages - 1:
                    logger.info(f"Достигнута последняя страница ({total_pages})")
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
