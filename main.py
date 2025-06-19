from src.api import HH, ParserError
from pprint import pprint


def user_interaction():
    platforms = ["HeadHunter"]
    print(platforms)
    keyword = input("Введите ключевое слово для поиска: ")
    max_pages = int(input("Максимальное количество страниц для поиска (по умолчанию 2): "))
    per_pages = int(input("Введите количество вакансий на странице (по умолчанию 100): "))
    area = int(input("ID региона, см.API.HH (Москва - 1, по умолчанию Россия [ID] = 113): "))
    salary_from = int(input("Минимальная зарплата (по умолчанию 0): "))
    salary_to = int(input("Максимальная зарплата (по умолчанию 500000): "))

    # top_n = int(input("Введите количество вакансий для вывода в топ N: "))
    # filter_words = input("Введите ключевые слова для фильтрации вакансий: ").split()
    # salary_range = input("Введите диапазон зарплат: ") # Пример: 100000 - 150000

    try:
        with HH(timeout=15) as hh_parser:
            vacancies = hh_parser.load_vacancies(
                keyword = keyword,
                max_pages = max_pages,
                per_page = per_pages,
                area = area,
                salary_from = salary_from,
                salary_to= salary_to
            )
            print(f"Найдено {len(vacancies)} вакансий")
            pprint(vacancies)

    except ParserError as e:
        print(f"Ошибка парсера: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")


    # filtered_vacancies = filter_vacancies(vacancies_list, filter_words)
    #
    # ranged_vacancies = get_vacancies_by_salary(filtered_vacancies, salary_range)
    #
    # sorted_vacancies = sort_vacancies(ranged_vacancies)
    # top_vacancies = get_top_vacancies(sorted_vacancies, top_n)
    # print_vacancies(top_vacancies)


if __name__ == "__main__":
    user_interaction()



#
#
#
# # Создание экземпляра класса для работы с API сайтов с вакансиями
# hh_api = HH()
#
# # Получение вакансий с hh.ru в формате JSON
# hh_vacancies = hh_api.load_vacancies("Python")
#
# # Преобразование набора данных из JSON в список объектов
# vacancies_list = Vacancy.cast_to_object_list(hh_vacancies)
#
# # Пример работы контструктора класса с одной вакансией
# vacancy = Vacancy("Python Developer", "<https://hh.ru/vacancy/123456>", "100 000-150 000 руб.", "Требования: опыт работы от 3 лет...")
#
# # Сохранение информации о вакансиях в файл
# json_saver = JSONSaver()
# json_saver.add_vacancy(vacancy)
# json_saver.delete_vacancy(vacancy)
#
# # Функция для взаимодействия с пользователем
#
