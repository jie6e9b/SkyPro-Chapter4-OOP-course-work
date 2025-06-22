from typing import List
from src.api import HH
from src.vacancy import Vacancy
from src.storage import JSONStorage


class UserInterface:
    """
    Класс пользовательского интерфейса для работы с вакансиями через консоль.
    """
    def __init__(self) -> None:
        self.api = HH()
        self.storage = JSONStorage()

    def run(self) -> None:
        """Главное меню программы"""
        while True:
            print("\n=== СИСТЕМА ПОИСКА ВАКАНСИЙ ===")
            print("1. Поиск новых вакансий на HH.ru")
            print("2. Просмотр сохраненных вакансий")
            print("3. Топ N вакансий по зарплате")
            print("4. Поиск по ключевому слову в описании")
            print("5. Очистить сохраненные вакансии")
            print("0. Выход")

            choice = input("\nВыберите действие: ").strip()

            if choice == "1":
                self._search_new_vacancies()
            elif choice == "2":
                self._show_saved_vacancies()
            elif choice == "3":
                self._show_top_vacancies()
            elif choice == "4":
                self._search_by_keyword()
            elif choice == "5":
                self._clear_vacancies()
            elif choice == "0":
                print("До свидания!")
                break
            else:
                print("Неверный выбор!")

    # Константы конфигурации
    SEARCH_CONFIG = {
        'MAX_PAGES': {'default': 3, 'min': 1, 'max': 20},
        'PER_PAGE': {'default': 100, 'min': 1, 'max': 100},
        'AREAS': {
            'all': 0,
            'russia': 113,
            'moscow': 1,
            'spb': 2
        }
    }

    def _search_new_vacancies(self) -> None:
        """Поиск новых вакансий через API"""
        try:
            # Получение поискового запроса
            keyword = self._get_search_keyword()
            if not keyword:
                return

            # Получение параметров поиска
            search_params = self._get_search_parameters()

            print(f"🔍 Ищем вакансии по запросу '{keyword}'...")

            # Получаем данные от API
            raw_vacancies = self.api.load_vacancies(
                keyword,
                max_pages=search_params['max_pages'],
                per_page=search_params['per_page'],
                area=search_params['area'],
                salary_from=search_params['salary_from'],
                salary_to=search_params['salary_to']
            )

            # Преобразуем в объекты Vacancy
            vacancies = [Vacancy.from_hh_dict(data) for data in raw_vacancies]

            if vacancies:
                # Сохраняем в файл
                self.storage.add_vacancies(vacancies)
                print(f"Найдeno и сохранено {len(vacancies)} вакансий")

                # Показываем первые 5
                self._display_vacancies(vacancies[:5])

            else:
                print("Вакансии не найдены")

        except Exception as e:
            print(f"❌ Ошибка при поиске вакансий: {e}")
            return None

    def _get_search_keyword(self) -> str:
        """Получение и валидация поискового запроса"""
        while True:
            keyword = input("📝 Введите поисковый запрос: ").strip()
            if keyword:
                return keyword
            print("⚠️ Запрос не может быть пустым! Попробуйте еще раз.")

    def _get_search_parameters(self) -> dict:
        """Получение параметров поиска с валидацией"""
        return {
            'max_pages': self._get_int_input(
                "📄 Введите максимальное количество страниц",
                default=3,
                min_val=1,
                max_val=20
            ),
            'per_page': self._get_int_input(
                "📊 Введите количество вакансий на странице",
                default=100,
                min_val=1,
                max_val=100
            ),
            'area': self._get_int_input(
                "🌍 Введите ID места работы (113-Россия, 1-Москва, см. API HH)",
                default=None,
                min_val=1,
                allow_none=True
            ),
            'salary_from': self._get_int_input(
                "💰 Введите минимальную зарплату",
                default=None,
                min_val=0,
                allow_none=True
            ),
            'salary_to': self._get_int_input(
                "💰 Введите максимальную зарплату",
                default=None,
                min_val=0,
                allow_none=True
            )
        }

    def _get_int_input(self, prompt: str, default: int | None = None, min_val: int | None = None,
                       max_val: int | None = None, allow_none: bool = False) -> int | None:
        """Универсальная функция получения числового ввода с проверками"""
        default_text = f" (по умолчанию: {default})" if default is not None else ""
        full_prompt = f"{prompt}{default_text}: "

        while True:
            try:
                user_input = input(full_prompt).strip()

                # Если пустой ввод и есть значение по умолчанию
                if not user_input:
                    if default is not None:
                        return default
                    elif allow_none:
                        return None
                    else:
                        print("⚠️ Значение обязательно для заполнения!")
                        continue

                # Преобразование в число
                value = int(user_input)

                # Валидация диапазона
                if min_val is not None and value < min_val:
                    print(f"⚠️ Значение должно быть не менее {min_val}")
                    continue

                if max_val is not None and value > max_val:
                    print(f"⚠️ Значение должно быть не более {max_val}")
                    continue

                return value

            except ValueError:
                print("⚠️ Введите корректное число!")

    def _show_saved_vacancies(self) -> None:
        """Показать все сохраненные вакансии"""
        vacancies = self.storage.get_vacancies()
        if vacancies:
            print(f"\nВсего сохранено {len(vacancies)} вакансий:")
            self._display_vacancies(vacancies)
        else:
            print("Сохраненных вакансий нет")

    def _show_top_vacancies(self) -> None:
        """Показать топ N вакансий по зарплате"""
        try:
            n = int(input("Введите количество вакансий для показа: "))
            vacancies = self.storage.get_vacancies()

            if vacancies:
                # Сортируем по убыванию зарплаты
                top_vacancies = sorted(vacancies, reverse=True)[:n]
                print(f"\nТоп {n} вакансий по зарплате:")
                self._display_vacancies(top_vacancies)
            else:
                print("Сохраненных вакансий нет")

        except ValueError:
            print("Введите корректное число!")

    def _search_by_keyword(self) -> None:
        """Поиск по ключевому слову в описании"""
        keyword = input("Введите ключевое слово для поиска: ").strip()
        if keyword:
            vacancies = self.storage.get_vacancies(keyword=keyword)
            if vacancies:
                print(f"\nНайдено {len(vacancies)} вакансий с ключевым словом '{keyword}':")
                self._display_vacancies(vacancies)
            else:
                print(f"Вакансий с ключевым словом '{keyword}' не найдено")

    def _clear_vacancies(self) -> None:
        """Очистить сохраненные вакансии"""
        confirm = input("Вы уверены, что хотите удалить все вакансии? (да/нет): ")
        if confirm.lower() in ['да', 'yes', 'y']:
            self.storage.clear_storage()
            print("Все вакансии удалены")

    def _display_vacancies(self, vacancies: List[Vacancy]) -> None:
        """Отобразить список вакансий"""
        for i, vacancy in enumerate(vacancies, 1):
            salary_info = self._format_salary(vacancy)
            print(f"\n{i}. {vacancy.title}")
            print(f"   Зарплата: {salary_info}")
            print(f"   Ссылка: {vacancy.url}")
            print(f"   Описание: {vacancy.description[:100]}...")

    def _format_salary(self, vacancy: Vacancy) -> str:
        """Форматирование зарплаты для отображения"""
        if vacancy.salary_from > 0 and vacancy.salary_to > 0:
            return f"{vacancy.salary_from} - {vacancy.salary_to} {vacancy.currency}"
        elif vacancy.salary_from > 0:
            return f"от {vacancy.salary_from} {vacancy.currency}"
        elif vacancy.salary_to > 0:
            return f"до {vacancy.salary_to} {vacancy.currency}"
        else:
            return "Не указана"
