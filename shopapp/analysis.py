"""
Модуль для анализа и визуализации данных.
Использует pandas, matplotlib, seaborn, networkx для различных анализов.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from db import get_all_orders, get_all_clients, get_all_products
from typing import List
from models import Order, Client, Product

def top_clients_by_orders():
    """Получить топ 5 клиентов по количеству заказов с использованием pandas."""
    orders = [o for o in get_all_orders() if o.client is not None]
    if not orders:
        print("Нет заказов")  # Оставляем, если нужно уведомление об ошибке
        return

    try:
        df = pd.DataFrame([{'client_id': o.client.id, 'client_name': o.client.name} for o in orders if o.client])
        if df.empty:
            print("Нет данных о клиентах")  # Оставляем, если нужно
            return

        top = df['client_id'].value_counts().head(5)
        top_df = top.reset_index()
        top_df.columns = ['client_id', 'count']
        top_df = top_df.merge(df[['client_id', 'client_name']].drop_duplicates(), on='client_id', how='left')

        # Убрали print-ы отсюда
        # print("Топ 5 клиентов по заказам:")
        # print(top_df)

        if not top_df.empty:
            plt.figure(figsize=(10, 6))
            sns.barplot(data=top_df, x='client_name', y='count', hue='client_name', palette='viridis', legend=False)
            plt.title("Топ 5 клиентов по количеству заказов")
            plt.xlabel("Клиент")
            plt.ylabel("Количество заказов")
            plt.xticks(rotation=45)
            plt.show()
        else:
            print("Нет данных для графика")  # Оставляем, если нужно
    except Exception as e:
        print(f"Ошибка в top_clients_by_orders: {str(e)}")

def plot_order_dynamics():
    """Построить динамику заказов по датам."""
    orders = get_all_orders()
    if not orders:
        print("Нет заказов")
        return

    df = pd.DataFrame([{'date': o.date} for o in orders])
    df['date'] = pd.to_datetime(df['date'])
    df_grouped = df.groupby('date').size().reset_index(name='count')

    plt.figure()
    sns.lineplot(data=df_grouped, x='date', y='count', marker='o', color='green')
    plt.title("Динамика заказов")
    plt.show()

def plot_client_graph():
    """Построить граф связей клиентов с товарами."""
    orders = [o for o in get_all_orders() if o.client is not None]
    if not orders:
        print("Нет заказов")
        return

    G = nx.Graph()

    # Добавляем узлы клиентов и товаров
    clients = {c.id: c.name for c in get_all_clients() if c.id}
    products = {p.id: p.name for p in get_all_products() if p.id}

    for client_id, client_name in clients.items():
        G.add_node(client_name, bipartite=0)  # 0 для клиентов

    for product_id, product_name in products.items():
        G.add_node(product_name, bipartite=1)  # 1 для товаров

    # Добавляем ребра между клиентами и товарами
    for order in orders:
        client_name = order.client.name
        for item in order.items:
            if item.product:
                product_name = item.product.name
                G.add_edge(client_name, product_name)

    if G.number_of_nodes() > 0:
        # Bipartite layout
        client_nodes = [n for n, d in G.nodes(data=True) if d['bipartite'] == 0]
        pos = nx.bipartite_layout(G, client_nodes)
        plt.figure(figsize=(12, 8))
        nx.draw(G, pos, with_labels=True, node_color=['lightblue' if d['bipartite']==0 else 'lightgreen' for n, d in G.nodes(data=True)], edge_color='gray')
        plt.title("Граф связей клиентов и товаров")
        plt.show()
    else:
        print("Нет данных для графа")