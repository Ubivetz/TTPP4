import unittest
from eshop_lab2 import Product, ShoppingCart


class TestEShopSystem(unittest.TestCase):
    def setUp(self):
        # Ініціалізація об'єктів для тестування
        self.product1 = Product(name='Ноутбук', price=25000.00, available_amount=10)
        self.product2 = Product(name='Смартфон', price=12500.50, available_amount=15)
        self.product3 = Product(name='Навушники', price=2000.00, available_amount=0)
        self.cart = ShoppingCart()

    def tearDown(self):
        # Очищення ресурсів після тестів
        self.cart.clear()

    # 1. Тестування властивостей продукту
    def test_product_properties(self):
        self.assertEqual(self.product1.name, 'Ноутбук')
        self.assertEqual(self.product1.price, 25000.00)
        self.assertEqual(self.product1.available_amount, 10)

    # 2. Тестування методу перевірки доступності продукту
    def test_product_availability(self):
        self.assertTrue(self.product1.is_available(5))
        self.assertTrue(self.product1.is_available(10))
        self.assertFalse(self.product1.is_available(11))
        self.assertFalse(self.product3.is_available(1))

    # 3. Тестування методу купівлі продукту
    def test_product_buy(self):
        initial_amount = self.product1.available_amount
        purchase_amount = 3
        self.product1.buy(purchase_amount)
        self.assertEqual(self.product1.available_amount, initial_amount - purchase_amount)

    # 4. Тестування рівності об'єктів Product
    def test_product_equality(self):
        product1_copy = Product(name='Ноутбук', price=30000.00, available_amount=5)
        different_product = Product(name='Інший ноутбук', price=25000.00, available_amount=10)

        self.assertEqual(self.product1, product1_copy)
        self.assertNotEqual(self.product1, different_product)

    # 5. Тестування хешування об'єктів Product
    def test_product_hash(self):
        product_dict = {self.product1: 'value1', self.product2: 'value2'}
        self.assertEqual(product_dict[self.product1], 'value1')
        self.assertEqual(product_dict[self.product2], 'value2')

    # 6. Тестування додавання продукту до кошика
    def test_cart_add_product(self):
        self.cart.add_product(self.product1, 5)
        self.assertTrue(self.cart.contains_product(self.product1))
        self.assertEqual(self.cart.get_product_quantity(self.product1), 5)

        # Тестування обробки помилок
        with self.assertRaises(ValueError):
            self.cart.add_product(None, 5)

        with self.assertRaises(ValueError):
            self.cart.add_product(self.product1, "5")

        with self.assertRaises(ValueError):
            self.cart.add_product(self.product1, 20)

    # 7. Тестування видалення продукту з кошика
    def test_cart_remove_product(self):
        self.cart.add_product(self.product1, 5)
        self.assertTrue(self.cart.contains_product(self.product1))

        self.cart.remove_product(self.product1)
        self.assertFalse(self.cart.contains_product(self.product1))

        # Перевіряємо, що видалення неіснуючого продукту не викликає помилку
        self.cart.remove_product(self.product2)

    # 8. Тестування обчислення загальної вартості кошика
    def test_cart_calculate_total(self):
        self.cart.add_product(self.product1, 2)  # 2 * 25000 = 50000
        self.cart.add_product(self.product2, 1)  # 1 * 12500.50 = 12500.50

        expected_total = 2 * self.product1.price + 1 * self.product2.price
        self.assertEqual(self.cart.calculate_total(), expected_total)

    # 9. Тестування оновлення кількості продукту в кошику
    def test_cart_update_quantity(self):
        self.cart.add_product(self.product1, 2)
        self.assertEqual(self.cart.get_product_quantity(self.product1), 2)

        self.cart.update_product_quantity(self.product1, 5)
        self.assertEqual(self.cart.get_product_quantity(self.product1), 5)

        # Перевірка на помилку при перевищенні доступної кількості
        with self.assertRaises(ValueError):
            self.cart.update_product_quantity(self.product1, 20)

        # Перевірка на помилку при оновленні неіснуючого продукту
        with self.assertRaises(ValueError):
            self.cart.update_product_quantity(self.product3, 1)

    # 10. Тестування оформлення замовлення з кошика
    def test_cart_submit_order(self):
        self.cart.add_product(self.product1, 3)
        self.cart.add_product(self.product2, 2)

        initial_amount1 = self.product1.available_amount
        initial_amount2 = self.product2.available_amount

        # Виконуємо замовлення
        self.cart.submit_cart_order()

        # Перевіряємо зміну кількості продуктів
        self.assertEqual(self.product1.available_amount, initial_amount1 - 3)
        self.assertEqual(self.product2.available_amount, initial_amount2 - 2)

        # Перевіряємо, що кошик порожній після оформлення замовлення
        self.assertFalse(self.cart.contains_product(self.product1))
        self.assertFalse(self.cart.contains_product(self.product2))


if __name__ == '__main__':
    unittest.main()