## Описание проекта

Это прототип промышленной системы учета заказов, клиентов и товаров с графическим интерфейсом на Tkinter, базой данных SQLite и анализом данных с использованием pandas, matplotlib, seaborn и networkx.

## Структура проекта

- models.py: Классы данных (Client, Product, Order и т.д.).
- db.py: Работа с базой данных SQLite (CRUD операции).
- gui.py: Графический интерфейс на Tkinter.
- analysis.py: Функции анализа и визуализации данных.
- main.py: Точка входа.
- test_models.py: Unit-тесты для models.py.
- test_analysis.py: Unit-тесты для analysis.py.

## Установка

1. Установите Python 3.12+.
2. Установите библиотеки: `pip install pandas matplotlib seaborn networkx tkinter sqlite3`.


## Использование
- Запустите `python main.py`.
- Добавляйте клиентов, товары, заказы через GUI.
- Анализируйте данные во вкладке "Анализ".
- Тестируйте: `python -m unittest test_models.py` и `python -m unittest test_analysis.py`.

Документация кода в docstrings (numpydoc стиль). Для генерации docs используйте Sphinx: `sphinx-quickstart` и настройте.
