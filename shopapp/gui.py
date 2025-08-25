"""
Модуль для графического интерфейса пользователя с использованием Tkinter.
Предоставляет формы для добавления клиентов, заказов, просмотра данных и т.д.
Теперь с вкладками, таблицами, фильтрами, кнопками для импорта/экспорта, удаления и изменения.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog, filedialog
import re
import sqlite3
import datetime
from models import Client, Product, Order, OrderItem
from db import (add_client, add_product, add_order, get_all_clients, get_all_orders, get_all_products,
                get_client_by_id, get_product_by_id, update_product, update_client, delete_client,
                delete_product, reindex_clients, reindex_products, delete_order, reindex_orders,
                export_clients_to_csv, import_clients_from_csv, export_products_to_csv, import_products_from_csv,
                export_orders_to_csv, import_orders_from_csv, export_clients_to_json, import_clients_from_json,
                export_products_to_json, import_products_from_json, export_orders_to_json, import_orders_from_json)
from analysis import top_clients_by_orders, plot_order_dynamics, plot_client_graph
from typing import List

def validate_email(email: str) -> bool:
    """Проверить email с использованием регулярного выражения."""
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Проверить телефон с использованием регулярного выражения."""
    pattern = r'^\+?[\d\s-]{10,15}$'
    return bool(re.match(pattern, phone))

class OrderManagementApp:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Система учета заказов")
        self.root.geometry("800x600")  # Установить размер окна
        self.root.configure(bg='white')  # Белый фон окна

        # Стиль для элементов
        style = ttk.Style()
        style.configure("TLabel", font=("Arial", 12), background='white', foreground='black')
        style.configure("TEntry", font=("Arial", 12), fieldbackground='white', foreground='black')
        style.configure("TButton", font=("Arial", 12, "bold"), background='white', foreground='black')  # Белый фон, черный текст
        style.configure("Treeview", font=("Arial", 11), background='white', foreground='black', fieldbackground='white')
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background='#D3D3D3', foreground='black')

        # Вкладки
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        # Вкладка Клиенты
        self.clients_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.clients_tab, text='Клиенты')
        self.setup_clients_tab()

        # Вкладка Товары
        self.products_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.products_tab, text='Товары')
        self.setup_products_tab()

        # Вкладка Заказы
        self.orders_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.orders_tab, text='Заказы')
        self.setup_orders_tab()

        # Вкладка Анализ
        self.analysis_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_tab, text='Анализ')
        self.setup_analysis_tab()

        # Вкладка Импорт/Экспорт
        self.io_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.io_tab, text='Импорт/Экспорт')
        self.setup_io_tab()

        # Переменные для выбора в заказе
        self.selected_client = None
        self.selected_products = []

        # Для редактирования
        self.editing_client_id = None
        self.editing_product_id = None

    def setup_clients_tab(self):
        """Вкладка для клиентов."""
        # Форма добавления/редактирования
        form_frame = ttk.Frame(self.clients_tab)
        form_frame.pack(side='left', padx=10, pady=10, fill='y')

        ttk.Label(form_frame, text="Имя").pack(pady=5)
        self.client_name = ttk.Entry(form_frame)
        self.client_name.pack(pady=5)

        ttk.Label(form_frame, text="Email").pack(pady=5)
        self.client_email = ttk.Entry(form_frame)
        self.client_email.pack(pady=5)

        ttk.Label(form_frame, text="Телефон").pack(pady=5)
        self.client_phone = ttk.Entry(form_frame)
        self.client_phone.pack(pady=5)

        ttk.Label(form_frame, text="Адрес").pack(pady=5)
        self.client_address = ttk.Entry(form_frame)
        self.client_address.pack(pady=5)

        ttk.Button(form_frame, text="Сохранить клиента", command=self.save_client).pack(pady=10)

        # Кнопки изменения и удаления
        ttk.Button(form_frame, text="Изменить клиента", command=self.load_selected_client).pack(pady=5)
        ttk.Button(form_frame, text="Удалить клиента", command=self.delete_selected_client).pack(pady=5)

        # Фильтр
        ttk.Label(form_frame, text="Фильтр по имени").pack(pady=5)
        self.client_filter = ttk.Entry(form_frame)
        self.client_filter.pack(pady=5)
        ttk.Button(form_frame, text="Применить фильтр", command=self.update_clients_table).pack(pady=5)

        # Таблица
        self.clients_tree = ttk.Treeview(self.clients_tab, columns=('ID', 'Имя', 'Email', 'Телефон', 'Адрес'), show='headings')
        self.clients_tree.heading('ID', text='ID', command=lambda: self.sort_treeview(self.clients_tree, 'ID', False))
        self.clients_tree.heading('Имя', text='Имя', command=lambda: self.sort_treeview(self.clients_tree, 'Имя', False))
        self.clients_tree.heading('Email', text='Email', command=lambda: self.sort_treeview(self.clients_tree, 'Email', False))
        self.clients_tree.heading('Телефон', text='Телефон', command=lambda: self.sort_treeview(self.clients_tree, 'Телефон', False))
        self.clients_tree.heading('Адрес', text='Адрес', command=lambda: self.sort_treeview(self.clients_tree, 'Адрес', False))
        self.clients_tree.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        ttk.Button(self.clients_tab, text="Обновить таблицу", command=self.update_clients_table).pack(pady=10)
        self.update_clients_table()  # Начальная загрузка

    def setup_products_tab(self):
        """Вкладка для товаров."""
        # Форма добавления/редактирования
        form_frame = ttk.Frame(self.products_tab)
        form_frame.pack(side='left', padx=10, pady=10, fill='y')

        ttk.Label(form_frame, text="Название").pack(pady=5)
        self.product_name = ttk.Entry(form_frame)
        self.product_name.pack(pady=5)

        ttk.Label(form_frame, text="Цена").pack(pady=5)
        self.product_price = ttk.Entry(form_frame)
        self.product_price.pack(pady=5)

        ttk.Label(form_frame, text="Категория").pack(pady=5)
        self.product_category = ttk.Entry(form_frame)
        self.product_category.pack(pady=5)

        ttk.Label(form_frame, text="Количество").pack(pady=5)
        self.product_quantity = ttk.Entry(form_frame)
        self.product_quantity.pack(pady=5)

        ttk.Button(form_frame, text="Сохранить товар", command=self.save_product).pack(pady=10)

        # Кнопки изменения и удаления
        ttk.Button(form_frame, text="Изменить товар", command=self.load_selected_product).pack(pady=5)
        ttk.Button(form_frame, text="Удалить товар", command=self.delete_selected_product).pack(pady=5)

        # Фильтр
        ttk.Label(form_frame, text="Фильтр по названию").pack(pady=5)
        self.product_filter = ttk.Entry(form_frame)
        self.product_filter.pack(pady=5)
        ttk.Button(form_frame, text="Применить фильтр", command=self.update_products_table).pack(pady=5)

        # Таблица
        self.products_tree = ttk.Treeview(self.products_tab, columns=('ID', 'Название', 'Цена', 'Категория', 'Количество'), show='headings')
        self.products_tree.heading('ID', text='ID', command=lambda: self.sort_treeview(self.products_tree, 'ID', False))
        self.products_tree.heading('Название', text='Название', command=lambda: self.sort_treeview(self.products_tree, 'Название', False))
        self.products_tree.heading('Цена', text='Цена', command=lambda: self.sort_treeview(self.products_tree, 'Цена', False))
        self.products_tree.heading('Категория', text='Категория', command=lambda: self.sort_treeview(self.products_tree, 'Категория', False))
        self.products_tree.heading('Количество', text='Количество', command=lambda: self.sort_treeview(self.products_tree, 'Количество', False))
        self.products_tree.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        ttk.Button(self.products_tab, text="Обновить таблицу", command=self.update_products_table).pack(pady=10)
        self.update_products_table()

    def setup_orders_tab(self):
        """Вкладка для заказов."""
        # Подвкладки для создания и просмотра
        orders_notebook = ttk.Notebook(self.orders_tab)
        orders_notebook.pack(fill='both', expand=True)

        # Подвкладка Создание заказа
        create_order_frame = ttk.Frame(orders_notebook)
        orders_notebook.add(create_order_frame, text='Создать заказ')

        # Таблица клиентов
        ttk.Label(create_order_frame, text="Выберите клиента:").pack(pady=5)
        self.order_clients_tree = ttk.Treeview(create_order_frame, columns=('ID', 'Имя', 'Email'), show='headings', height=5)
        self.order_clients_tree.heading('ID', text='ID')
        self.order_clients_tree.heading('Имя', text='Имя')
        self.order_clients_tree.heading('Email', text='Email')
        self.order_clients_tree.pack(fill='x', padx=10, pady=5)
        self.order_clients_tree.bind('<<TreeviewSelect>>', self.on_select_client)

        # Таблица товаров
        ttk.Label(create_order_frame, text="Выберите товары (удерживайте Ctrl для нескольких):").pack(pady=5)
        self.order_products_tree = ttk.Treeview(create_order_frame, columns=('ID', 'Название', 'Цена', 'Количество'), show='headings', selectmode='extended')
        self.order_products_tree.heading('ID', text='ID')
        self.order_products_tree.heading('Название', text='Название')
        self.order_products_tree.heading('Цена', text='Цена')
        self.order_products_tree.heading('Количество', text='Количество')
        self.order_products_tree.pack(fill='both', expand=True, padx=10, pady=5)
        self.order_products_tree.bind('<<TreeviewSelect>>', self.on_select_products)

        ttk.Button(create_order_frame, text="Создать заказ", command=self.save_order).pack(pady=10)

        self.update_order_clients_table()
        self.update_order_products_table()

        # Подвкладка Просмотр заказов
        view_orders_frame = ttk.Frame(orders_notebook)
        orders_notebook.add(view_orders_frame, text='Просмотр заказов')

        # Фильтр по дате
        filter_frame = ttk.Frame(view_orders_frame)
        filter_frame.pack(pady=5)

        ttk.Label(filter_frame, text="Фильтр по дате (YYYY-MM-DD)").pack(side='left', padx=5)
        self.order_filter = ttk.Entry(filter_frame)
        self.order_filter.pack(side='left', padx=5)
        ttk.Button(filter_frame, text="Применить", command=self.update_orders_table).pack(side='left', padx=5)

        # Таблица с скроллом
        tree_frame = ttk.Frame(view_orders_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.orders_tree = ttk.Treeview(tree_frame, columns=('ID', 'Клиент', 'Дата', 'Сумма', 'Товары'), show='headings')
        self.orders_tree.heading('ID', text='ID', command=lambda: self.sort_treeview(self.orders_tree, 'ID', False))
        self.orders_tree.heading('Клиент', text='Клиент', command=lambda: self.sort_treeview(self.orders_tree, 'Клиент', False))
        self.orders_tree.heading('Дата', text='Дата', command=lambda: self.sort_treeview(self.orders_tree, 'Дата', False))
        self.orders_tree.heading('Сумма', text='Сумма', command=lambda: self.sort_treeview(self.orders_tree, 'Сумма', False))
        self.orders_tree.heading('Товары', text='Товары', command=lambda: self.sort_treeview(self.orders_tree, 'Товары', False))

        self.orders_tree.column('ID', width=50)
        self.orders_tree.column('Клиент', width=150)
        self.orders_tree.column('Дата', width=100)
        self.orders_tree.column('Сумма', width=100)
        self.orders_tree.column('Товары', width=300, stretch=True)  # Широкая колонка для товаров

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.orders_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.orders_tree.xview)
        self.orders_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.orders_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        ttk.Button(view_orders_frame, text="Обновить таблицу", command=self.update_orders_table).pack(pady=5)
        ttk.Button(view_orders_frame, text="Удалить заказ", command=self.delete_selected_order).pack(pady=5)

        self.update_orders_table()

    def setup_analysis_tab(self):
        """Вкладка для анализа."""
        ttk.Button(self.analysis_tab, text="Топ 5 клиентов", command=top_clients_by_orders).pack(pady=10)
        ttk.Button(self.analysis_tab, text="Динамика заказов", command=plot_order_dynamics).pack(pady=10)
        ttk.Button(self.analysis_tab, text="Граф клиентов", command=plot_client_graph).pack(pady=10)

    def setup_io_tab(self):
        """Вкладка для импорта/экспорта."""
        io_frame = ttk.Frame(self.io_tab)
        io_frame.pack(padx=10, pady=10)

        # Экспорт
        ttk.Label(io_frame, text="Экспорт").pack(pady=5)
        ttk.Button(io_frame, text="Экспорт клиентов CSV", command=lambda: self.export_to_file(export_clients_to_csv)).pack(pady=5)
        ttk.Button(io_frame, text="Экспорт товаров CSV", command=lambda: self.export_to_file(export_products_to_csv)).pack(pady=5)
        ttk.Button(io_frame, text="Экспорт заказов CSV", command=lambda: self.export_to_file(export_orders_to_csv)).pack(pady=5)
        ttk.Button(io_frame, text="Экспорт клиентов JSON", command=lambda: self.export_to_file(export_clients_to_json)).pack(pady=5)
        ttk.Button(io_frame, text="Экспорт товаров JSON", command=lambda: self.export_to_file(export_products_to_json)).pack(pady=5)
        ttk.Button(io_frame, text="Экспорт заказов JSON", command=lambda: self.export_to_file(export_orders_to_json)).pack(pady=5)

        # Импорт
        ttk.Label(io_frame, text="Импорт").pack(pady=5)
        ttk.Button(io_frame, text="Импорт клиентов CSV", command=lambda: self.import_from_file(import_clients_from_csv)).pack(pady=5)
        ttk.Button(io_frame, text="Импорт товаров CSV", command=lambda: self.import_from_file(import_products_from_csv)).pack(pady=5)
        ttk.Button(io_frame, text="Импорт заказов CSV", command=lambda: self.import_from_file(import_orders_from_csv)).pack(pady=5)
        ttk.Button(io_frame, text="Импорт клиентов JSON", command=lambda: self.import_from_file(import_clients_from_json)).pack(pady=5)
        ttk.Button(io_frame, text="Импорт товаров JSON", command=lambda: self.import_from_file(import_products_from_json)).pack(pady=5)
        ttk.Button(io_frame, text="Импорт заказов JSON", command=lambda: self.import_from_file(import_orders_from_json)).pack(pady=5)

    def export_to_file(self, export_func):
        """Общий метод для экспорта с выбором файла."""
        filename = filedialog.asksaveasfilename(defaultextension=".csv" if "csv" in export_func.__name__ else ".json")
        if filename:
            try:
                export_func(filename)
                messagebox.showinfo("Успех", "Экспорт завершен")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def import_from_file(self, import_func):
        """Общий метод для импорта с выбором файла."""
        filename = filedialog.askopenfilename()
        if filename:
            try:
                import_func(filename)
                messagebox.showinfo("Успех", "Импорт завершен")
                self.update_all_tables()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def update_all_tables(self):
        """Обновить все таблицы после импорта."""
        self.update_clients_table()
        self.update_products_table()
        self.update_orders_table()
        self.update_order_clients_table()
        self.update_order_products_table()

    def save_client(self):
        """Сохранить или обновить клиента."""
        try:
            name = self.client_name.get()
            email = self.client_email.get()
            phone = self.client_phone.get()
            address = self.client_address.get()

            if not validate_email(email):
                raise ValueError("Неверный email")
            if not validate_phone(phone):
                raise ValueError("Неверный телефон")

            client = Client(name, email, phone, address)
            if self.editing_client_id:
                client.id = self.editing_client_id
                update_client(client)
                messagebox.showinfo("Успех", "Клиент обновлен")
                self.editing_client_id = None
            else:
                add_client(client)
                messagebox.showinfo("Успех", "Клиент добавлен")

            self.clear_client_form()
            self.update_clients_table()
            self.update_order_clients_table()
            self.update_orders_table()
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def load_selected_client(self):
        """Загрузить выбранного клиента в форму для редактирования."""
        selected = self.clients_tree.selection()
        if selected:
            item = self.clients_tree.item(selected[0])
            client_id = item['values'][0]
            client = get_client_by_id(client_id)
            if client:
                self.client_name.delete(0, tk.END)
                self.client_name.insert(0, client.name)
                self.client_email.delete(0, tk.END)
                self.client_email.insert(0, client.email)
                self.client_phone.delete(0, tk.END)
                self.client_phone.insert(0, client.phone)
                self.client_address.delete(0, tk.END)
                self.client_address.insert(0, client.address)
                self.editing_client_id = client.id

    def delete_selected_client(self):
        """Удалить выбранного клиента."""
        selected = self.clients_tree.selection()
        if selected:
            item = self.clients_tree.item(selected[0])
            client_id = item['values'][0]
            try:
                delete_client(client_id)
                reindex_clients()
                messagebox.showinfo("Успех", "Клиент удален")
                self.update_clients_table()
                self.update_order_clients_table()
                self.update_orders_table()
            except sqlite3.IntegrityError:
                messagebox.showerror("Ошибка", "Нельзя удалить клиента с заказами")

    def clear_client_form(self):
        """Очистить форму клиента."""
        self.client_name.delete(0, tk.END)
        self.client_email.delete(0, tk.END)
        self.client_phone.delete(0, tk.END)
        self.client_address.delete(0, tk.END)

    def save_product(self):
        """Сохранить или обновить товар."""
        try:
            name = self.product_name.get()
            price = float(self.product_price.get())
            category = self.product_category.get()
            quantity = int(self.product_quantity.get())

            product = Product(name, price, category, quantity)
            if self.editing_product_id:
                product.id = self.editing_product_id
                update_product(product)
                messagebox.showinfo("Успех", "Товар обновлен")
                self.editing_product_id = None
            else:
                add_product(product)
                messagebox.showinfo("Успех", "Товар добавлен")

            self.clear_product_form()
            self.update_products_table()
            self.update_order_products_table()
        except ValueError:
            messagebox.showerror("Ошибка", "Неверные данные")

    def load_selected_product(self):
        """Загрузить выбранный товар в форму для редактирования."""
        selected = self.products_tree.selection()
        if selected:
            item = self.products_tree.item(selected[0])
            product_id = item['values'][0]
            product = get_product_by_id(product_id)
            if product:
                self.product_name.delete(0, tk.END)
                self.product_name.insert(0, product.name)
                self.product_price.delete(0, tk.END)
                self.product_price.insert(0, str(product.price))
                self.product_category.delete(0, tk.END)
                self.product_category.insert(0, product.category)
                self.product_quantity.delete(0, tk.END)
                self.product_quantity.insert(0, str(product.quantity))
                self.editing_product_id = product.id

    def delete_selected_product(self):
        """Удалить выбранный товар."""
        selected = self.products_tree.selection()
        if selected:
            item = self.products_tree.item(selected[0])
            product_id = item['values'][0]
            try:
                delete_product(product_id)
                reindex_products()
                messagebox.showinfo("Успех", "Товар удален")
                self.update_products_table()
                self.update_order_products_table()
                self.update_orders_table()
            except sqlite3.IntegrityError:
                messagebox.showerror("Ошибка", "Нельзя удалить товар с заказами")

    def clear_product_form(self):
        """Очистить форму товара."""
        self.product_name.delete(0, tk.END)
        self.product_price.delete(0, tk.END)
        self.product_category.delete(0, tk.END)
        self.product_quantity.delete(0, tk.END)

    def save_order(self):
        """Сохранить новый заказ."""
        try:
            if not self.selected_client:
                raise ValueError("Выберите клиента")
            if not self.selected_products:
                raise ValueError("Выберите хотя бы один товар")

            items = []
            for product in self.selected_products:
                qty = simpledialog.askinteger("Количество", f"Введите количество для {product.name} (доступно: {product.quantity}):", minvalue=1, maxvalue=product.quantity)
                if qty is None:
                    raise ValueError("Отмена ввода количества")
                if qty > product.quantity:
                    raise ValueError(f"Недостаточно {product.name} на складе")
                items.append(OrderItem(product, qty))
                product.quantity -= qty
                update_product(product)

            order = Order(self.selected_client, items)
            add_order(order)
            messagebox.showinfo("Успех", "Заказ добавлен")

            self.update_orders_table()
            self.update_products_table()
            self.update_order_products_table()

            # Сброс выбора
            self.selected_client = None
            self.selected_products = []
            self.order_clients_tree.selection_remove(self.order_clients_tree.selection())
            self.order_products_tree.selection_remove(self.order_products_tree.selection())
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def on_select_client(self, event):
        """Обработчик выбора клиента."""
        selected = self.order_clients_tree.selection()
        if selected:
            item = self.order_clients_tree.item(selected[0])
            client_id = item['values'][0]
            self.selected_client = get_client_by_id(client_id)

    def on_select_products(self, event):
        """Обработчик выбора товаров."""
        selected = self.order_products_tree.selection()
        self.selected_products = []
        for sel in selected:
            item = self.order_products_tree.item(sel)
            product_id = item['values'][0]
            product = get_product_by_id(product_id)
            if product:
                self.selected_products.append(product)

    def update_clients_table(self):
        """Обновить таблицу клиентов с фильтром."""
        filter_text = self.client_filter.get().lower()
        self.clients_tree.delete(*self.clients_tree.get_children())
        clients = get_all_clients()
        for client in clients:
            if filter_text in client.name.lower():
                self.clients_tree.insert('', 'end', values=(client.id, client.name, client.email, client.phone, client.address))

    def update_products_table(self):
        """Обновить таблицу товаров с фильтром."""
        filter_text = self.product_filter.get().lower()
        self.products_tree.delete(*self.products_tree.get_children())
        products = get_all_products()
        for product in products:
            if filter_text in product.name.lower():
                self.products_tree.insert('', 'end', values=(product.id, product.name, product.price, product.category, product.quantity))

    def update_orders_table(self):
        """Обновить таблицу заказов с сортировкой и фильтром."""
        filter_date = self.order_filter.get()
        self.orders_tree.delete(*self.orders_tree.get_children())
        orders = get_all_orders()
        if filter_date:
            try:
                filter_dt = datetime.date.fromisoformat(filter_date)
                orders = [o for o in orders if o.date == filter_dt]
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты")
                return

        # Сортировка по дате с использованием quicksort
        sorted_orders = self.quicksort_orders(orders, key=lambda o: o.date)

        for order in sorted_orders:
            if order.client is None:
                client_name = "Неизвестный"
            else:
                client_name = order.client.name
            product_str = ', '.join(f"{item.product.name} x {item.quantity}" for item in order.items if item.product)
            self.orders_tree.insert('', 'end', values=(order.id, client_name, str(order.date), order.calculate_total(), product_str))

    def delete_selected_order(self):
        """Удалить выбранный заказ."""
        selected = self.orders_tree.selection()
        if selected:
            item = self.orders_tree.item(selected[0])
            order_id = item['values'][0]
            delete_order(order_id)
            reindex_orders()
            messagebox.showinfo("Успех", "Заказ удален")
            self.update_orders_table()

    def update_order_clients_table(self):
        """Обновить таблицу клиентов для заказа."""
        self.order_clients_tree.delete(*self.order_clients_tree.get_children())
        clients = get_all_clients()
        for client in clients:
            self.order_clients_tree.insert('', 'end', values=(client.id, client.name, client.email))

    def update_order_products_table(self):
        """Обновить таблицу товаров для заказа."""
        self.order_products_tree.delete(*self.order_products_tree.get_children())
        products = get_all_products()
        for product in products:
            self.order_products_tree.insert('', 'end', values=(product.id, product.name, product.price, product.quantity))

    def quicksort_orders(self, orders: List[Order], key) -> List[Order]:
        """Рекурсивная быстрая сортировка для заказов."""
        if len(orders) <= 1:
            return orders
        pivot = orders[len(orders) // 2]
        left = [o for o in orders if key(o) < key(pivot)]
        middle = [o for o in orders if key(o) == key(pivot)]
        right = [o for o in orders if key(o) > key(pivot)]
        return self.quicksort_orders(left, key) + middle + self.quicksort_orders(right, key)

    def sort_treeview(self, tree, col, descending):
        """Сортировка Treeview по колонке."""
        data = [(tree.set(item, col), item) for item in tree.get_children('')]
        # Попытка сортировать как числа, если возможно
        try:
            data.sort(key=lambda t: float(t[0]), reverse=descending)
        except ValueError:
            data.sort(key=lambda t: t[0], reverse=descending)

        for index, (val, item) in enumerate(data):
            tree.move(item, '', index)

        # Переключить направление сортировки
        tree.heading(col, command=lambda: self.sort_treeview(tree, col, not descending))