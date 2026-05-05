import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
import urllib.request
import urllib.error

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("600x500")

        # API ключ (замените на свой)
        self.api_key = "YOUR_API_KEY"  # Замените на ваш API-ключ

        self.history_file = "conversion_history.json"
        self.history = []
        self.load_history()

        self.setup_ui()

    def setup_ui(self):
        # Заголовок
        title_label = tk.Label(self.root, text="Конвертер валют",
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # Фрейм для выбора валют и ввода суммы
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=20)

        # Выбор валюты «из»
        tk.Label(input_frame, text="Из:").grid(row=0, column=0, padx=5)
        self.from_currency = ttk.Combobox(input_frame,
                                           values=self.get_currencies(),
                                           state="readonly",
                                   width=10)
        self.from_currency.grid(row=0, column=1, padx=5)
        self.from_currency.set("USD")

        # Выбор валюты «в»
        tk.Label(input_frame, text="В:").grid(row=0, column=2, padx=5)
        self.to_currency = ttk.Combobox(input_frame,
                                         values=self.get_currencies(),
                                         state="readonly",
                   width=10)
        self.to_currency.grid(row=0, column=3, padx=5)
        self.to_currency.set("RUB")

        # Поле ввода суммы
        tk.Label(input_frame, text="Сумма:").grid(row=1, column=0, padx=5, pady=10)
        self.amount_entry = tk.Entry(input_frame, width=15)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=10)

        # Кнопка конвертации
        convert_btn = tk.Button(input_frame, text="Конвертировать",
                               command=self.convert_currency,
                               bg="#4CAF50", fg="white")
        convert_btn.grid(row=1, column=2, columnspan=2, pady=10, padx=5)

        # Метка результата
        self.result_label = tk.Label(self.root, text="",
                            font=("Arial", 12))
        self.result_label.pack(pady=10)

        # Таблица истории
        history_label = tk.Label(self.root, text="История конвертаций:",
                         font=("Arial", 12, "bold"))
        history_label.pack()

        columns = ("Дата", "Сумма", "Из", "В", "Результат")
        self.history_tree = ttk.Treeview(self.root, columns=columns, show="headings", height=8)

        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)

        self.history_tree.pack(pady=10, padx=20, fill="both", expand=True)

        # Кнопка очистки истории
        clear_btn = tk.Button(self.root, text="Очистить историю",
                   command=self.clear_history,
                   bg="#f44336", fg="white")
        clear_btn.pack(pady=5)

    def get_currencies(self):
        """Возвращает список популярных валют"""
        return ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "RUB"]

    def get_exchange_rate(self, from_curr, to_curr):
        """Получает актуальный курс через API с использованием urllib"""
        try:
            url = f"https://api.exchangerate-api.com/v4/latest/{from_curr}"
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())

            if to_curr in data['rates']:
                return data['rates'][to_curr]
            else:
                raise Exception(f"Валюта {to_curr} не найдена в ответах API")
        except urllib.error.URLError as e:
            messagebox.showerror("Ошибка сети", f"Не удалось подключиться к API: {e}")
            return None
        except json.JSONDecodeError as e:
            messagebox.showerror("Ошибка данных", f"Ошибка разбора JSON: {e}")
            return None
        except Exception as e:
            messagebox.showerror("Ошибка API", f"Не удалось получить курс: {e}")
            return None

    def convert_currency(self):
        try:
            # Проверка ввода
            amount = float(self.amount_entry.get())
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом!")
                return

            from_curr = self.from_currency.get()
            to_curr = self.to_currency.get()

            # Получение курса через API
            rate = self.get_exchange_rate(from_curr, to_curr)
            if rate is None:
                return

            # Расчёт
            result = amount * rate

            # Отображение результата
            self.result_label.config(
                text=f"{amount:.2f} {from_curr} = {result:.2f} {to_curr}"
            )

            # Сохранение в историю
            conversion = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "amount": amount,
                "from": from_curr,
                "to": to_curr,
                "result": result
            }
            self.add_to_history(conversion)

        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректную сумму!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
                self.update_history_table()
            except Exception as e:
                self.history = []
                messagebox.showwarning("Предупреждение", f"Не удалось загрузить историю: {e}")
        else:
            self.history = []

    def save_history(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")


    def add_to_history(self, conversion):
        self.history.append(conversion)
        self.save_history()
        self.update_history_table()

    def update_history_table(self):
        # Очистка таблицы
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

                # Заполнение таблицы (последние 10 записей)
        for record in reversed(self.history[-10:]):
            self.history_tree.insert("", "end", values=(
                record["date"],
                f"{record['amount']:.2f}",
                record["from"],
                record["to"],
                f"{record['result']:.2f}"
            ))

    def clear_history(self):
        self.history = []
        self.save_history()
        self.update_history_table()

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()
