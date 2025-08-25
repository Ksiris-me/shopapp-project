""""
Точка входа в программу для системы учета заказов.
Этот модуль инициализирует и запускает графический интерфейс приложения.
"""

import tkinter as tk
from gui import OrderManagementApp

if __name__ == "__main__":
    root = tk.Tk()
    app = OrderManagementApp(root)
    root.mainloop()
    "Ага"