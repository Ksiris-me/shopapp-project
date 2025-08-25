import unittest
from models import Client, Product, Order, OrderItem, DiscountOrder
import datetime

class TestModels(unittest.TestCase):
    def test_client(self):
        client = Client("Test", "test@email.com", "+123456789")
        self.assertEqual(client.name, "Test")
        self.assertEqual(client.email, "test@email.com")

    def test_product(self):
        product = Product("Item", 10.0, "Cat", 5)
        self.assertEqual(product.name, "Item")
        self.assertEqual(product.price, 10.0)

    def test_order(self):
        client = Client("Test", "test@email.com", "+123456789")
        product = Product("Item", 10.0)
        item = OrderItem(product, 2)
        order = Order(client, [item])
        self.assertEqual(order.calculate_total(), 20.0)

    def test_discount_order(self):
        client = Client("Test", "test@email.com", "+123456789")
        product = Product("Item", 10.0)
        item = OrderItem(product, 2)
        order = DiscountOrder(client, [item], discount=0.1)
        self.assertEqual(order.calculate_total(), 18.0)

if __name__ == '__main__':
    unittest.main()