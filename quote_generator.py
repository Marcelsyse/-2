import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime

# Предопределённые цитаты
PREDEFINED_QUOTES = [
    {"text": "Будь изменением, которое ты хочешь увидеть в мире.", "author": "Махатма Ганди", "topic": "Мотивация"},
    {"text": "Жизнь — это то, что с тобой происходит, пока ты строишь планы.", "author": "Джон Леннон", "topic": "Жизнь"},
    {"text": "Воображение важнее знания.", "author": "Альберт Эйнштейн", "topic": "Наука"},
    {"text": "Ты упускаешь 100% выстрелов, которые не делаешь.", "author": "Уэйн Гретцки", "topic": "Мотивация"},
    {"text": "Сложности должны заставлять тебя действовать, а не останавливать.", "author": "Мэри Кей Эш", "topic": "Успех"},
    {"text": "Единственный способ делать великую работу — любить то, что ты делаешь.", "author": "Стив Джобс", "topic": "Работа"},
    {"text": "Не считай дни, делай так, чтобы дни считались.", "author": "Мухаммед Али", "topic": "Мотивация"},
]

HISTORY_FILE = "quotes_history.json"

class QuoteGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Quote Generator")
        self.root.geometry("700x600")
        self.root.resizable(False, False)

        # Загружаем историю
        self.history = self.load_history()

        # Создаём GUI
        self.create_widgets()

        # Текущая цитата
        self.current_quote = None

    def create_widgets(self):
        # Рамка для отображения цитаты
        quote_frame = tk.Frame(self.root, padx=20, pady=20)
        quote_frame.pack(fill=tk.X)

        self.quote_label = tk.Label(quote_frame, text="Нажми 'Сгенерировать цитату'", 
                                    font=("Arial", 14, "italic"), wraplength=600, justify="center")
        self.quote_label.pack()

        self.author_label = tk.Label(quote_frame, text="", font=("Arial", 12), fg="gray")
        self.author_label.pack(pady=(5,0))

        # Кнопка генерации
        self.generate_btn = tk.Button(self.root, text="Сгенерировать цитату", 
                                      command=self.generate_quote, bg="#4CAF50", fg="white",
                                      font=("Arial", 12), padx=10, pady=5)
        self.generate_btn.pack(pady=10)

        # Фильтры
        filter_frame = tk.LabelFrame(self.root, text="Фильтры", padx=10, pady=10)
        filter_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(filter_frame, text="Автор:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.author_var = tk.StringVar()
        self.author_combo = ttk.Combobox(filter_frame, textvariable=self.author_var, width=30)
        self.author_combo.grid(row=0, column=1, padx=5, pady=5)
        self.update_author_list()

        tk.Label(filter_frame, text="Тема:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.topic_var = tk.StringVar()
        self.topic_combo = ttk.Combobox(filter_frame, textvariable=self.topic_var, width=30)
        self.topic_combo.grid(row=1, column=1, padx=5, pady=5)
        self.update_topic_list()

        self.filter_btn = tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        self.filter_btn.grid(row=2, column=0, columnspan=2, pady=10)

        self.clear_filter_btn = tk.Button(filter_frame, text="Сбросить фильтры", command=self.clear_filters)
        self.clear_filter_btn.grid(row=3, column=0, columnspan=2)

        # Добавление новой цитаты
        add_frame = tk.LabelFrame(self.root, text="Добавить новую цитату", padx=10, pady=10)
        add_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(add_frame, text="Текст:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.new_text = tk.Entry(add_frame, width=50)
        self.new_text.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(add_frame, text="Автор:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.new_author = tk.Entry(add_frame, width=30)
        self.new_author.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        tk.Label(add_frame, text="Тема:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.new_topic = tk.Entry(add_frame, width=20)
        self.new_topic.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        self.add_btn = tk.Button(add_frame, text="Добавить цитату", command=self.add_quote, bg="#2196F3", fg="white")
        self.add_btn.grid(row=3, column=0, columnspan=2, pady=5)

        # История
        history_frame = tk.LabelFrame(self.root, text="История цитат", padx=10, pady=10)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.history_listbox = tk.Listbox(history_frame, height=10)
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(history_frame, orient="vertical", command=self.history_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_listbox.config(yscrollcommand=scrollbar.set)

        self.update_history_display()

    def update_author_list(self):
        authors = sorted(set(q["author"] for q in PREDEFINED_QUOTES))
        self.author_combo['values'] = [""] + authors

    def update_topic_list(self):
        topics = sorted(set(q["topic"] for q in PREDEFINED_QUOTES))
        self.topic_combo['values'] = [""] + topics

    def generate_quote(self):
        quotes = PREDEFINED_QUOTES
        # Применяем фильтры
        author_filter = self.author_var.get().strip()
        topic_filter = self.topic_var.get().strip()

        if author_filter:
            quotes = [q for q in quotes if q["author"] == author_filter]
        if topic_filter:
            quotes = [q for q in quotes if q["topic"] == topic_filter]

        if not quotes:
            messagebox.showwarning("Нет цитат", "Нет цитат, соответствующих фильтрам.")
            return

        self.current_quote = random.choice(quotes).copy()
        self.quote_label.config(text=f"“{self.current_quote['text']}”")
        self.author_label.config(text=f"— {self.current_quote['author']}")

        # Добавляем в историю с датой
        self.current_quote["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append(self.current_quote)
        self.save_history()
        self.update_history_display()

    def apply_filter(self):
        self.generate_quote()

    def clear_filters(self):
        self.author_var.set("")
        self.topic_var.set("")
        self.generate_quote()

    def add_quote(self):
        text = self.new_text.get().strip()
        author = self.new_author.get().strip()
        topic = self.new_topic.get().strip()

        if not text or not author or not topic:
            messagebox.showerror("Ошибка", "Все поля (текст, автор, тема) обязательны для заполнения.")
            return

        new_quote = {"text": text, "author": author, "topic": topic}
        PREDEFINED_QUOTES.append(new_quote)
        self.update_author_list()
        self.update_topic_list()
        messagebox.showinfo("Успех", "Цитата добавлена!")
        self.new_text.delete(0, tk.END)
        self.new_author.delete(0, tk.END)
        self.new_topic.delete(0, tk.END)

    def update_history_display(self):
        self.history_listbox.delete(0, tk.END)
        for quote in self.history:
            display = f"[{quote['timestamp']}] {quote['text'][:60]}... — {quote['author']} ({quote['topic']})"
            self.history_listbox.insert(tk.END, display)

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_history(self):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = QuoteGeneratorApp(root)
    root.mainloop()
