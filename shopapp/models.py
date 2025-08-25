"""
Модуль, содержащий модели данных для клиентов, товаров и заказов.
В этом модуле определяются классы, представляющие основные сущности системы.
Добавлен подкласс DiscountOrder для демонстрации полиморфизма.
"""

import datetime
from typing import List

class Person:
    def __init__(self, name: str):
        self._name = name  # Инкапсуляция: приватный атрибут

    @property
    def name(self) -> str:
        """Получить имя."""
        return self._name

    @name.setter
    def name(self, value: str):
        """Установить имя."""
        self._name = value

class Client(Person):
    def __init__(self, name: str, email: str, phone: str, address: str = ''):
        super().__init__(name)
        self.id = None
        self.email = email
        self.phone = phone
        self.address = address

    def __str__(self) -> str:
        return f"Клиент(ID={self.id}, Имя={self.name}, Email={self.email})"

class Product:
    def __init__(self, name: str, price: float, category: str = 'General', quantity: int = 0):
        self.id = None
        self.name = name
        self.price = price
        self.category = category
        self.quantity = quantity

    def __str__(self) -> str:
        return f"Товар(ID={self.id}, Название={self.name}, Цена={self.price}, Количество={self.quantity})"

class OrderItem:
    def __init__(self, product: Product, quantity: int):
        self.product = product
        self.quantity = quantity

class Order:
    def __init__(self, client: Client, items: List[OrderItem], date: datetime.date = None):
        self.id = None
        self.client = client
        self.items = items
        self.date = date or datetime.date.today()

    def calculate_total(self) -> float:
        """
        Рассчитать общую стоимость заказа.
        """
        return sum(item.product.price * item.quantity for item in self.items if item.product is not None)

    def __str__(self) -> str:
        return f"Заказ(ID={self.id}, КлиентID={self.client.id}, Дата={self.date}, Сумма={self.calculate_total()})"

class DiscountOrder(Order):
    """
    Подкласс Order с скидкой для демонстрации полиморфизма.

    Параметры
    ----------
    discount : float
        Процент скидки (0-1).
    """

    def __init__(self, client: Client, items: List[OrderItem], date: datetime.date = None, discount: float = 0.1):
        super().__init__(client, items, date)
        self.discount = discount

    def calculate_total(self) -> float:
        """Переопределенный метод с учетом скидки."""
        total = super().calculate_total()
        return total * (1 - self.discount)