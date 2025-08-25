import unittest
from unittest.mock import patch, MagicMock
from analysis import top_clients_by_orders, plot_order_dynamics, plot_client_graph
from models import Order, Client, Product, OrderItem
import datetime

class TestAnalysis(unittest.TestCase):
    @patch('analysis.get_all_orders')
    @patch('analysis.get_all_clients')
    @patch('analysis.plt')
    def test_top_clients_by_orders(self, mock_plt, mock_get_clients, mock_get_orders):
        client1 = Client("Client1", "c1@email.com", "+1")
        client1.id = 1
        client2 = Client("Client2", "c2@email.com", "+2")
        client2.id = 2
        order1 = Order(client1, [])
        order2 = Order(client2, [])
        mock_get_orders.return_value = [order1, order2]
        mock_get_clients.return_value = [client1, client2]
        top_clients_by_orders()
        mock_plt.figure.assert_called()
        mock_plt.show.assert_called()

    @patch('analysis.get_all_orders')
    @patch('analysis.plt')
    @patch('analysis.sns')
    def test_plot_order_dynamics(self, mock_sns, mock_plt, mock_get_orders):
        order = Order(MagicMock(), [], datetime.date.today())
        mock_get_orders.return_value = [order]
        plot_order_dynamics()
        mock_plt.figure.assert_called()
        mock_plt.show.assert_called()

    @patch('analysis.get_all_orders')
    @patch('analysis.get_all_clients')
    @patch('analysis.get_all_products')
    @patch('analysis.plt')
    @patch('analysis.nx')
    def test_plot_client_graph(self, mock_nx, mock_plt, mock_get_products, mock_get_clients, mock_get_orders):
        client = Client("Client", "c@email.com", "+1")
        client.id = 1
        product = Product("Item", 10.0)
        product.id = 1
        item = OrderItem(product, 1)
        order = Order(client, [item])
        mock_get_orders.return_value = [order]
        mock_get_clients.return_value = [client]
        mock_get_products.return_value = [product]
        plot_client_graph()
        mock_plt.figure.assert_called()
        mock_plt.show.assert_called()

if __name__ == '__main__':
    unittest.main()