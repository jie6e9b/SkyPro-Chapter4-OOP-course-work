from src.utils import UserInterface


def main():
    """Точка входа в программу"""
    try:
        ui = UserInterface()
        ui.run()
    except KeyboardInterrupt:
        print("\n\nПрограмма завершена пользователем")
    except Exception as e:
        print(f"Критическая ошибка: {e}")


if __name__ == "__main__":
    main()
