"""
Модуль для операций с базой данных с использованием SQLite.
Обрабатывает CRUD-операции для клиентов, товаров и заказов.
Теперь включает импорт/экспорт в CSV и JSON.
"""

import sqlite3
import datetime
from models import Client, Product, Order, OrderItem
from typing import List, Optional
import csv
import json
import os

DB_NAME = 'order_management.db'  # Имя файла базы данных

def init_db():
    """Инициализировать базу данных и создать таблицы, если они не существуют."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        address TEXT
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        category TEXT,
        quantity INTEGER NOT NULL DEFAULT 0
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        FOREIGN KEY (client_id) REFERENCES clients(id)
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_products (
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (product_id) REFERENCES products(id),
        PRIMARY KEY (order_id, product_id)
    )
    ''')
    # Проверить и добавить столбец quantity в order_products, если отсутствует
    cursor.execute("PRAGMA table_info(order_products)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'quantity' not in columns:
        cursor.execute('ALTER TABLE order_products ADD COLUMN quantity INTEGER NOT NULL DEFAULT 1')
    conn.commit()
    conn.close()

def add_client(client: Client):
    """Добавить клиента в базу данных."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO clients (name, email, phone, address) VALUES (?, ?, ?, ?)',
                   (client.name, client.email, client.phone, client.address))
    client.id = cursor.lastrowid
    conn.commit()
    conn.close()

def update_client(client: Client):
    """Обновить клиента в базу данных."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE clients SET name=?, email=?, phone=?, address=? WHERE id=?',
                   (client.name, client.email, client.phone, client.address, client.id))
    conn.commit()
    conn.close()

def delete_client(client_id: int):
    """Удалить клиента из базы данных."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM clients WHERE id=?', (client_id,))
    conn.commit()
    conn.close()

def reindex_clients():
    """Переиндексировать ID клиентов после удаления."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM clients ORDER BY id')
    ids = [row[0] for row in cursor.fetchall()]
    for new_id, old_id in enumerate(ids, 1):
        if new_id == old_id:
            continue
        # Временно обновить на отрицательные значения
        cursor.execute('UPDATE orders SET client_id = ? WHERE client_id = ?', (-new_id, old_id))
        cursor.execute('UPDATE clients SET id = ? WHERE id = ?', (-new_id, old_id))
    # Сделать положительными
    cursor.execute('UPDATE orders SET client_id = -client_id WHERE client_id < 0')
    cursor.execute('UPDATE clients SET id = -id WHERE id < 0')
    # Обновить последовательность AUTOINCREMENT
    if ids:
        try:
            cursor.execute("UPDATE sqlite_sequence SET seq = ? WHERE name = 'clients'", (len(ids),))
        except sqlite3.OperationalError:
            pass  # Если таблица sqlite_sequence не существует, игнорируем
    conn.commit()
    conn.close()

def add_product(product: Product):
    """Добавить товар в базу данных."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO products (name, price, category, quantity) VALUES (?, ?, ?, ?)',
                   (product.name, product.price, product.category, product.quantity))
    product.id = cursor.lastrowid
    conn.commit()
    conn.close()

def update_product(product: Product):
    """Обновить товар в базу данных."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE products SET name=?, price=?, category=?, quantity=? WHERE id=?',
                   (product.name, product.price, product.category, product.quantity, product.id))
    conn.commit()
    conn.close()

def delete_product(product_id: int):
    """Удалить товар из базы данных."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE id=?', (product_id,))
    conn.commit()
    conn.close()

def reindex_products():
    """Переиндексировать ID товаров после удаления."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM products ORDER BY id')
    ids = [row[0] for row in cursor.fetchall()]
    for new_id, old_id in enumerate(ids, 1):
        if new_id == old_id:
            continue
        # Временно обновить на отрицательные значения
        cursor.execute('UPDATE order_products SET product_id = ? WHERE product_id = ?', (-new_id, old_id))
        cursor.execute('UPDATE products SET id = ? WHERE id = ?', (-new_id, old_id))
    # Сделать положительными
    cursor.execute('UPDATE order_products SET product_id = -product_id WHERE product_id < 0')
    cursor.execute('UPDATE products SET id = -id WHERE id < 0')
    # Обновить последовательность AUTOINCREMENT
    if ids:
        try:
            cursor.execute("UPDATE sqlite_sequence SET seq = ? WHERE name = 'products'", (len(ids),))
        except sqlite3.OperationalError:
            pass  # Если таблица sqlite_sequence не существует, игнорируем
    conn.commit()
    conn.close()

def add_order(order: Order):
    """Добавить заказ в базу данных."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO orders (client_id, date) VALUES (?, ?)',
                   (order.client.id, order.date.isoformat()))
    order.id = cursor.lastrowid
    for item in order.items:
        cursor.execute('INSERT INTO order_products (order_id, product_id, quantity) VALUES (?, ?, ?)',
                       (order.id, item.product.id, item.quantity))
    conn.commit()
    conn.close()

def delete_order(order_id: int):
    """Удалить заказ из базы данных."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM order_products WHERE order_id=?', (order_id,))
    cursor.execute('DELETE FROM orders WHERE id=?', (order_id,))
    conn.commit()
    conn.close()

def reindex_orders():
    """Переиндексировать ID заказов после удаления."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM orders ORDER BY id')
    ids = [row[0] for row in cursor.fetchall()]
    for new_id, old_id in enumerate(ids, 1):
        if new_id == old_id:
            continue
        # Временно обновить на отрицательные значения
        cursor.execute('UPDATE order_products SET order_id = ? WHERE order_id = ?', (-new_id, old_id))
        cursor.execute('UPDATE orders SET id = ? WHERE id = ?', (-new_id, old_id))
    # Сделать положительными
    cursor.execute('UPDATE order_products SET order_id = -order_id WHERE order_id < 0')
    cursor.execute('UPDATE orders SET id = -id WHERE id < 0')
    # Обновить последовательность AUTOINCREMENT
    if ids:
        try:
            cursor.execute("UPDATE sqlite_sequence SET seq = ? WHERE name = 'orders'", (len(ids),))
        except sqlite3.OperationalError:
            pass
    conn.commit()
    conn.close()

def get_all_clients() -> List[Client]:
    """Получить всех клиентов из базы данных."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients')
    rows = cursor.fetchall()
    clients = []
    for row in rows:
        client = Client(name=row[1], email=row[2], phone=row[3], address=row[4])
        client.id = row[0]
        clients.append(client)
    conn.close()
    return clients

def get_all_products() -> List[Product]:
    """Получить все товары из базы данных."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    rows = cursor.fetchall()
    products = []
    for row in rows:
        product = Product(name=row[1], price=row[2], category=row[3], quantity=row[4])
        product.id = row[0]
        products.append(product)
    conn.close()
    return products

def get_all_orders() -> List[Order]:
    """Получить все заказы из базы данных."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders')
    order_rows = cursor.fetchall()
    orders = []
    for order_row in order_rows:
        client = get_client_by_id(order_row[1])
        cursor.execute('SELECT product_id, quantity FROM order_products WHERE order_id = ?', (order_row[0],))
        items = []
        for pid, qty in cursor.fetchall():
            p = get_product_by_id(pid)
            items.append(OrderItem(p, qty))
        order = Order(client, items, datetime.date.fromisoformat(order_row[2]))
        order.id = order_row[0]
        orders.append(order)
    conn.close()
    return orders

def get_client_by_id(client_id: int) -> Optional[Client]:
    """Получить клиента по ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (client_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        client = Client(name=row[1], email=row[2], phone=row[3], address=row[4])
        client.id = row[0]
        return client
    return None

def get_product_by_id(product_id: int) -> Optional[Product]:
    """Получить товар по ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        product = Product(name=row[1], price=row[2], category=row[3], quantity=row[4])
        product.id = row[0]
        return product
    return None

def export_clients_to_csv(filename: str = 'clients.csv'):
    """Экспортировать клиентов в CSV."""
    clients = get_all_clients()
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'name', 'email', 'phone', 'address'])
        for client in clients:
            writer.writerow([client.id, client.name, client.email, client.phone, client.address])

def import_clients_from_csv(filename: str = 'clients.csv'):
    """Импортировать клиентов из CSV."""
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Файл {filename} не найден")
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Пропустить заголовок
        for row in reader:
            client = Client(name=row[1], email=row[2], phone=row[3], address=row[4])
            add_client(client)  # id игнорируется, генерируется новый

def export_products_to_csv(filename: str = 'products.csv'):
    """Экспортировать товары в CSV."""
    products = get_all_products()
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'name', 'price', 'category', 'quantity'])
        for product in products:
            writer.writerow([product.id, product.name, product.price, product.category, product.quantity])

def import_products_from_csv(filename: str = 'products.csv'):
    """Импортировать товары из CSV."""
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Файл {filename} не найден")
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            product = Product(name=row[1], price=float(row[2]), category=row[3], quantity=int(row[4]))
            add_product(product)

def export_orders_to_csv(filename: str = 'orders.csv'):
    """Экспортировать заказы в CSV (упрощенно, без items)."""
    orders = get_all_orders()
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'client_id', 'date', 'items'])
        for order in orders:
            items_str = ';'.join(f"{item.product.id}:{item.quantity}" for item in order.items)
            writer.writerow([order.id, order.client.id, order.date.isoformat(), items_str])

def import_orders_from_csv(filename: str = 'orders.csv'):
    """Импортировать заказы из CSV."""
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Файл {filename} не найден")
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            client = get_client_by_id(int(row[1]))
            if not client:
                continue  # Пропустить, если клиент не найден
            date = datetime.date.fromisoformat(row[2])
            items = []
            for item_str in row[3].split(';'):
                pid, qty = item_str.split(':')
                product = get_product_by_id(int(pid))
                if product:
                    items.append(OrderItem(product, int(qty)))
            order = Order(client, items, date)
            add_order(order)

def export_clients_to_json(filename: str = 'clients.json'):
    """Экспортировать клиентов в JSON."""
    clients = get_all_clients()
    data = [{'id': c.id, 'name': c.name, 'email': c.email, 'phone': c.phone, 'address': c.address} for c in clients]
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def import_clients_from_json(filename: str = 'clients.json'):
    """Импортировать клиентов из JSON."""
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Файл {filename} не найден")
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for item in data:
            client = Client(name=item['name'], email=item['email'], phone=item['phone'], address=item.get('address', ''))
            add_client(client)

def export_products_to_json(filename: str = 'products.json'):
    """Экспортировать товары в JSON."""
    products = get_all_products()
    data = [{'id': p.id, 'name': p.name, 'price': p.price, 'category': p.category, 'quantity': p.quantity} for p in products]
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def import_products_from_json(filename: str = 'products.json'):
    """Импортировать товары из JSON."""
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Файл {filename} не найден")
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for item in data:
            product = Product(name=item['name'], price=item['price'], category=item.get('category', 'General'), quantity=item['quantity'])
            add_product(product)

def export_orders_to_json(filename: str = 'orders.json'):
    """Экспортировать заказы в JSON."""
    orders = get_all_orders()
    data = []
    for order in orders:
        items = [{'product_id': item.product.id, 'quantity': item.quantity} for item in order.items]
        data.append({'id': order.id, 'client_id': order.client.id, 'date': order.date.isoformat(), 'items': items})
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def import_orders_from_json(filename: str = 'orders.json'):
    """Импортировать заказы из JSON."""
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Файл {filename} не найден")
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for item in data:
            client = get_client_by_id(item['client_id'])
            if not client:
                continue
            date = datetime.date.fromisoformat(item['date'])
            items = []
            for i in item['items']:
                product = get_product_by_id(i['product_id'])
                if product:
                    items.append(OrderItem(product, i['quantity']))
            order = Order(client, items, date)
            add_order(order)

# Инициализировать БД при загрузке модуля
init_db()