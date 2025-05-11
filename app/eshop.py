"""Модуль для керування продуктами, кошиком і замовленнями в інтернет-магазині."""

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from services import ShippingService


class Product:
    """Клас, що представляє товар у магазині."""

    def __init__(self, name, price, available_amount):
        """
        Ініціалізує новий товар.

        :param name: Назва товару.
        :param price: Ціна за одиницю.
        :param available_amount: Кількість доступних одиниць.
        """
        self.name = name
        self.price = price
        self.available_amount = available_amount

    def is_available(self, requested_amount):
        """
        Перевіряє, чи доступна потрібна кількість товару.

        :param requested_amount: Бажана кількість.
        :return: True, якщо доступно.
        """
        return self.available_amount >= requested_amount

    def buy(self, requested_amount):
        """
        Зменшує кількість товару після покупки.

        :param requested_amount: Кількість для купівлі.
        """
        self.available_amount -= requested_amount

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return self.name != other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name


class ShoppingCart:
    """Клас для управління кошиком користувача."""

    def __init__(self):
        """Створює порожній кошик."""
        self.products = {}

    def contains_product(self, product):
        """
        Перевіряє, чи є продукт у кошику.

        :param product: Продукт для перевірки.
        :return: True, якщо є.
        """
        return product in self.products

    def calculate_total(self):
        """
        Обчислює загальну суму кошика.

        :return: Сума замовлення.
        """
        return sum(p.price * count for p, count in self.products.items())

    def add_product(self, product: Product, amount: int):
        """
        Додає продукт до кошика.

        :param product: Товар для додавання.
        :param amount: Кількість товару.
        :raises ValueError: Якщо товару недостатньо.
        """
        if not product.is_available(amount):
            raise ValueError(f"Product {product} has only {product.available_amount} items")
        self.products[product] = amount

    def remove_product(self, product):
        """
        Видаляє продукт з кошика.

        :param product: Продукт для видалення.
        """
        if product in self.products:
            del self.products[product]

    def submit_cart_order(self):
        """
        Оформлює замовлення і очищує кошик.

        :return: Список ID придбаних продуктів.
        """
        product_ids = []
        for product, count in self.products.items():
            product.buy(count)
            product_ids.append(str(product))
        self.products.clear()
        return product_ids


@dataclass
class Order:
    """Клас, що представляє замовлення."""

    cart: ShoppingCart
    shipping_service: ShippingService
    order_id: str = str(uuid.uuid4())

    def place_order(self, shipping_type, due_date: datetime = None):
        """
        Оформлює замовлення та викликає службу доставки.

        :param shipping_type: Тип доставки.
        :param due_date: Дата, до якої має бути виконана доставка.
        :return: Об'єкт доставки.
        """
        if not due_date:
            due_date = datetime.now(timezone.utc) + timedelta(seconds=3)
        product_ids = self.cart.submit_cart_order()
        print(due_date)
        return self.shipping_service.create_shipping(
            shipping_type, product_ids, self.order_id, due_date
        )


@dataclass
class Shipment:
    """Клас для відстеження доставки."""

    shipping_id: str
    shipping_service: ShippingService

    def check_shipping_status(self):
        """
        Перевіряє статус доставки.

        :return: Поточний статус доставки.
        """
        return self.shipping_service.check_status(self.shipping_id)
