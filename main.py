# main.py
import tkinter as tk
from tkinter import ttk, messagebox

# Импортируем наши модули моторов
import g4fc
import d20dtf

class EngineMasterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Интерактивный Модульный Руководство по Сборке v3.0")
        self.root.geometry("900x650")
        self.root.minsize(750, 550)
        
        style = ttk.Style()
        style.theme_use("clam")
        
        # Словарь для связи выбора в меню с модулями
        self.engines = {
            g4fc.NAME: g4fc,
            d20dtf.NAME: d20dtf
        }
        
        # --- ВЕРХНЯЯ ПАНЕЛЬ ВЫБОРА МОТОРА ---
        top_frame = ttk.Frame(root, padding=10)
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text="Мотор на стапеле:", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        
        self.engine_selector = ttk.Combobox(top_frame, values=list(self.engines.keys()), state="readonly", font=("Arial", 11), width=45)
        self.engine_selector.pack(side=tk.LEFT, padx=10)
        self.engine_selector.bind("<<ComboboxSelected>>", self.on_engine_change)
        
        # --- СИСТЕМА ВКЛАДОК ---
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Вкладка 1: Лаборатория
        self.tab_lab = ttk.Frame(self.notebook)
        self.text_lab = tk.Text(self.tab_lab, font=("Consolas", 11), wrap=tk.WORD, bg="#fcfdfc", padx=15, pady=15)
        self.setup_scrollable_text(self.tab_lab, self.text_lab)
        self.notebook.add(self.tab_lab, text=" 🔬 1. Лаборатория (Зазоры) ")
        
        # Вкладка 2: Конвейер сборки
        self.tab_steps = ttk.Frame(self.notebook)
        self.text_steps = tk.Text(self.tab_steps, font=("Consolas", 11), wrap=tk.WORD, bg="#fcfcfc", padx=15, pady=15)
        self.setup_scrollable_text(self.tab_steps, self.text_steps)
        self.notebook.add(self.tab_steps, text=" 🛠️ 2. Пошаговая сборка ")
        
        # Вкладка 3: Навесное оборудование
        self.tab_nav = ttk.Frame(self.notebook)
        self.text_nav = tk.Text(self.tab_nav, font=("Consolas", 11), wrap=tk.WORD, bg="#fcfcfd", padx=15, pady=15)
        self.setup_scrollable_text(self.tab_nav, self.text_nav)
        self.notebook.add(self.tab_nav, text=" ⚙️ 3. Навесное оборудование ")

        # --- НИЖНЯЯ ПАНЕЛЬ: ДИНАМИЧЕСКИЙ КАЛЬКУЛЯТОР КЛАПАНОВ ---
        self.calc_frame = ttk.LabelFrame(root, text=" 🧮 Калькулятор подбора стаканчиков клапанов (G4FC) ", padding=10)
        # Размещаем элементы внутри калькулятора
        ttk.Label(self.calc_frame, text="Тип:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.valve_type = ttk.Combobox(self.calc_frame, values=["Впуск", "Выпуск"], state="readonly", width=8, font=("Arial", 10))
        self.valve_type.current(0)
        self.valve_type.grid(row=0, column=1, padx=5)
        
        ttk.Label(self.calc_frame, text="Зазор щупом (мм):").grid(row=0, column=2, padx=5, sticky=tk.W)
        self.entry_measured = ttk.Entry(self.calc_frame, width=10, font=("Arial", 10))
        self.entry_measured.grid(row=0, column=3, padx=5)
        
        ttk.Label(self.calc_frame, text="Старый стакан (мм):").grid(row=0, column=4, padx=5, sticky=tk.W)
        self.entry_old = ttk.Entry(self.calc_frame, width=10, font=("Arial", 10))
        self.entry_old.grid(row=0, column=5, padx=5)
        
        btn_calc = ttk.Button(self.calc_frame, text="Рассчитать", command=self.run_valve_calculation)
        btn_calc.grid(row=0, column=6, padx=15)
        
        self.lbl_result = ttk.Label(self.calc_frame, text="Результат: —", font=("Arial", 11, "bold"), foreground="#2e7d32")
        self.lbl_result.grid(row=0, column=7, padx=10, sticky=tk.W)

        # Старт приложения
        self.engine_selector.current(0)
        self.on_engine_change(None)

    def setup_scrollable_text(self, parent_frame, text_widget):
        scrollbar = ttk.Scrollbar(parent_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def on_engine_change(self, event):
        """Переключает текстовые базы данных и показывает/скрывает калькулятор клапанов"""
        selected_name = self.engine_selector.get()
        module = self.engines[selected_name]
        
        # Обновляем вкладки данными из модулей
        self.text_lab.delete("1.0", tk.END)
        self.text_lab.insert(tk.END, module.LAB_DATA)
        
        self.text_steps.delete("1.0", tk.END)
        self.text_steps.insert(tk.END, module.STEPS_DATA)
        
        self.text_nav.delete("1.0", tk.END)
        self.text_nav.insert(tk.END, module.NAV_DATA)
        
        # Если выбран Солярис (G4FC) — показываем калькулятор клапанов, иначе скрываем
        if selected_name == g4fc.NAME:
            self.calc_frame.pack(fill=tk.X, padx=10, pady=10, side=tk.BOTTOM)
        else:
            self.calc_frame.pack_forget()

    def run_valve_calculation(self):
        """Запускает математический расчет из модуля g4fc"""
        v_type = self.valve_type.get()
        measured = self.entry_measured.get().strip()
        old = self.entry_old.get().strip()
        
        if not measured or not old:
            messagebox.showwarning("Внимание", "Заполните все поля для расчета!")
            return
            
        result = g4fc.calculate_valve(v_type, measured, old)
        self.lbl_result.config(text=f"Результат: {result}")

if __name__ == "__main__":
    root = tk.Tk()
    app = EngineMasterApp(root)
    root.mainloop()
