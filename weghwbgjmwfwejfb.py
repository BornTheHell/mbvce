import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import random
import string
import sqlite3
from PIL import Image, ImageTk
import time

conn = sqlite3.connect('lab_management_system.db')
cursor = conn.cursor()

# Добавление информации о расходах
expenses_data = [
    (2, 'Покупка химикатов', 1500),
    (2, 'Зарплата лаборанту', 2000),
    (2, 'Аренда лаборатории', 500),
    (2, 'Покупка оборудования', 3000),
    (2, 'Канцелярские товары', 200),
    (2, 'Электричество', 100),
    (2, 'Вода', 50),
    (2, 'Транспортные расходы', 300),
    (2, 'Сервисное обслуживание оборудования', 400),
    (2, 'Консультационные услуги', 250)
]

cursor.executemany("INSERT INTO expenses (user_id, expense_description, expense_amount) VALUES (?, ?, ?)", expenses_data)
conn.commit()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        full_name TEXT,
        photo_path TEXT
    )
''')

cursor.execute('''
    INSERT INTO users (username, password, role, full_name, photo_path) VALUES
    ('admin', '12345', 'администратор', 'Admin Adminov', 'admin.jpg'),
    ('accountant', 'password1', 'бухгалтер', 'Accountant User', 'bygalter.jpg'),
    ('lab_technician', 'password2', 'лаборант', 'Lab Technician', 'laborant.jpg'),
    ('researcher', 'password3', 'лаборант-исследователь', 'Researcher User', 'isledovatel.jpg')
''')

cursor.execute('UPDATE users SET role = ?, full_name = ? WHERE id = ?', ('бухгалтер', 'Бухгалтер Бухгалтеров', 2))
cursor.execute('UPDATE users SET role = ?, full_name = ? WHERE id = ?', ('лаборант', 'Лаборант Лабораторный', 3))
cursor.execute('UPDATE users SET role = ?, full_name = ? WHERE id = ?', ('лаборант-исследователь', 'Лаборант-исследователь Исследовательский', 4))

cursor.execute('''
    CREATE TABLE IF NOT EXISTS login_history (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        report_text TEXT,
        report_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS biomaterials (
        id INTEGER PRIMARY KEY,
        lab_technician_id INTEGER,
        biomaterial_type TEXT,
        accepted_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (lab_technician_id) REFERENCES users (id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        expense_description TEXT,
        expense_amount REAL,
        expense_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        invoice_description TEXT,
        invoice_amount REAL,
        invoice_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY,
        lab_technician_id INTEGER,
        service_name TEXT,
        service_description TEXT,
        service_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (lab_technician_id) REFERENCES users (id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS biomaterial_types (
        id INTEGER PRIMARY KEY,
        biomaterial_type TEXT
    )
''')

cursor.execute('''
    INSERT INTO biomaterial_types (biomaterial_type) VALUES
    ('Кровь'),
    ('Моча'),
    ('Слюна'),
    ('Ткань')
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS service_reports (
        id INTEGER PRIMARY KEY,
        service_id INTEGER,
        report_text TEXT,
        report_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (service_id) REFERENCES services (id)
    )
''')

conn.commit()

def login(user_type):
    def submit_login():
        entered_username = username_entry.get()
        entered_password = password_entry.get()
        cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (entered_username, entered_password))
        user = cursor.fetchone()

        if user:
            cursor.execute('INSERT INTO login_history (user_id) VALUES (?)', (user[0],))
            conn.commit()
            messagebox.showinfo("Успешный вход", f"Вход выполнен как {user_type}")
            login_window.destroy()
            show_user_panel(user_type, user)
        else:
            messagebox.showerror("Ошибка входа", "Неправильный логин или пароль")
            username_entry.delete(0, tk.END)
            password_entry.delete(0, tk.END)
            generate_captcha()

    def generate_captcha():
        captcha = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        captcha_label.config(text=f"Капча: {captcha}")
        captcha_window.deiconify()

    def check_captcha():
        entered_captcha = captcha_entry.get()
        if entered_captcha == captcha_label.cget("text").split(": ")[-1]:
            captcha_window.withdraw()
        else:
            messagebox.showerror("Ошибка капчи", "Неправильная капча")
            generate_captcha()

    roles_to_fio_index = {
        'администратор': 4,
        'бухгалтер': 4,
        'лаборант': 4,
        'лаборант-исследователь': 4
    }

    def perform_service(user_id, user_panel):
        service_name = tk.simpledialog.askstring("Выполнение услуги", "Введите название услуги:")
        service_description = tk.simpledialog.askstring("Выполнение услуги", "Введите описание услуги:")
    
        cursor.execute('INSERT INTO services (lab_technician_id, service_name, service_description) VALUES (?, ?, ?)',
                   (user_id, service_name, service_description))
        conn.commit()
    
        service_id = cursor.lastrowid  # Получаем ID только что добавленной услуги
    
        cursor.execute('INSERT INTO service_reports (service_id, report_text) VALUES (?, ?)', (service_id, "Услуга выполнена без отчета"))
        conn.commit()
    
        messagebox.showinfo("Выполнение услуги", "Услуга успешно выполнена!")

    def show_user_panel(user_role, user_data):
        user_panel = tk.Toplevel(root)
        user_panel.title(f"Панель {user_role}")
        print(user_data)  
        print(user_role)
        fio_index = roles_to_fio_index.get(user_role, None)
        if fio_index is not None and len(user_data) > fio_index:
            fio = user_data[fio_index]
        else:
            fio = "Неизвестное ФИО"
        tk.Label(user_panel, text=f"ФИО: {fio}").pack()

        tk.Label(user_panel, text=f"Роль: {user_role}").pack()

        photo_path = {
            'администратор': "C:\\capcha\\admin.jpg",
            'бухгалтер': "C:\\capcha\\bygalter.jpg",
            'лаборант': "C:\\capcha\\laborant.jpg",
            'лаборант-исследователь': "C:\\capcha\\isledovatel.jpg"
        }.get(user_role, None)

        if photo_path:
            try:
                image = Image.open(photo_path)
                profile_photo = ImageTk.PhotoImage(image)
                profile_photo_label = tk.Label(user_panel, image=profile_photo)
                profile_photo_label.image = profile_photo
                profile_photo_label.pack()
            except Exception as e:
                tk.Label(user_panel, text=f"Ошибка загрузки фото профиля: {e}").pack()

        if user_role == "бухгалтер":
            add_buttons_for_accountant(user_panel, user_data)

        elif user_role == "лаборант":
            add_buttons_for_lab_technician(user_panel, user_data, user_panel)

        elif user_role == "лаборант-исследователь":
            add_buttons_for_researcher(user_panel, user_data, user_panel)

        logout_button = tk.Button(user_panel, text="Выход", command=lambda: logout(user_panel))
        logout_button.pack()

    def add_buttons_for_accountant(parent, user):
        expenses_button = tk.Button(parent, text="Просмотреть расходы", command=lambda: show_expenses_table(user[0]))
        expenses_button.pack()

    def add_buttons_for_lab_technician(parent, user_data, another_panel):

        report_button = tk.Button(parent, text="Сформировать отчеты", command=lambda: show_reports(user_data[0]))
        report_button.pack()

        user_panel = another_panel  # просто пример, замените на соответствующий код
        service_button = tk.Button(parent, text="Выполнить услугу", command=lambda panel=user_panel: perform_service(user_data[0], panel))
        service_button.pack()
        start_timer(user_panel)


    def add_buttons_for_researcher(parent, user):
        analyzer_button = tk.Button(parent, text="Работать с анализатором", command=lambda: work_with_analyzer(user[0]))
        analyzer_button.pack()
        start_timer()

    def start_timer(user_panel):
        start_time = time.time()  
        end_time = start_time + 600

        def update_timer():
            current_time = time.time()
            remaining_time = end_time - current_time

            if remaining_time <= 0:
                timer_window.destroy()
                user_panel.destroy()  # Закрываем окно пользователя
                return

            timer_label.config(text=time.strftime("%H:%M:%S", time.gmtime(remaining_time)))

            if remaining_time <= 300:  
                messagebox.showinfo("Внимание", "До конца сессии осталось 5 минут!")

            root.after(1000, update_timer)

        timer_window = tk.Toplevel(root)
        timer_window.title("Таймер")
        timer_label = tk.Label(timer_window, text="", font=("Arial", 24))
        timer_label.pack(padx=20, pady=20)
        update_timer()

    def show_login_history(user_id):
        login_history_window = tk.Toplevel(root)
        login_history_window.title("История входа")
        cursor.execute('SELECT login_time FROM login_history WHERE user_id=? ORDER BY login_time DESC', (user_id,))
        login_history = cursor.fetchall()

        for i, login_time in enumerate(login_history):
            tk.Label(login_history_window, text=f"{i + 1}. {login_time[0]}").pack()

    def show_expenses_table(user_id):
        expenses_window = tk.Toplevel(root)
        expenses_window.title("Таблица расходов")
        print("Просмотр расходов вызван!")

        cursor.execute('SELECT expense_description, expense_amount, expense_time FROM expenses WHERE user_id=? ORDER BY expense_time DESC', (user_id,))
        expenses = cursor.fetchall()

        try:
            cursor.execute('SELECT id, user_id, expense_description, expense_amount, expense_time FROM expenses;')
            expenses = cursor.fetchall()
            
        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")

        for expense in expenses:
            

            tk.Label(expenses_window, text=f"ID: {expense[0]}").pack()
            tk.Label(expenses_window, text=f"Пользователь: {expense[1]}").pack()
            tk.Label(expenses_window, text=f"Описание: {expense[2]}").pack()
            tk.Label(expenses_window, text=f"Сумма: {expense[3]}").pack()
            tk.Label(expenses_window, text=f"Дата: {expense[4]}").pack()
            tk.Label(expenses_window, text="-------------------------").pack()

    def show_reports(user_id):
        reports_window = tk.Toplevel(root)
        reports_window.title("Отчеты по услугам")

        cursor.execute('''
            SELECT s.service_name, s.service_description, r.report_text, r.report_time
            FROM services s
            JOIN service_reports r ON s.id = r.service_id
            WHERE s.lab_technician_id = ?
            ORDER BY r.report_time DESC
        ''', (user_id,))
        reports = cursor.fetchall()

        for report in reports:
            tk.Label(reports_window, text=f"Название услуги: {report[0]}").pack()
            tk.Label(reports_window, text=f"Описание услуги: {report[1]}").pack()
            tk.Label(reports_window, text=f"Текст отчета: {report[2]}").pack()
            tk.Label(reports_window, text=f"Время создания отчета: {report[3]}").pack()
            tk.Label(reports_window, text="-------------------------").pack()

    def work_with_analyzer(user_id):
        messagebox.askquestion("Анализатор", "Отправить отчет в бухгалтерию?")

    login_window = tk.Toplevel(root)
    login_window.title(f"Вход {user_type}")

    username_label = tk.Label(login_window, text="Логин:")
    username_label.pack()
    username_entry = tk.Entry(login_window)
    username_entry.pack()

    password_label = tk.Label(login_window, text="Пароль:")
    password_label.pack()
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack()

    show_password_var = tk.IntVar()

    def toggle_password_visibility():
        password_entry.config(show="" if show_password_var.get() else "*")

    toggle_password_button = tk.Checkbutton(login_window, text="Показать пароль", variable=show_password_var, command=toggle_password_visibility)
    toggle_password_button.pack()

    submit_button = tk.Button(login_window, text="Войти", command=submit_login)
    submit_button.pack()

    captcha_window = tk.Toplevel(root)
    captcha_window.title("Капча")
    captcha_window.withdraw()

    captcha_label = tk.Label(captcha_window, text="")
    captcha_label.pack()

    captcha_entry = tk.Entry(captcha_window)
    captcha_entry.pack()

    captcha_submit = tk.Button(captcha_window, text="Подтвердить", command=check_captcha)
    captcha_submit.pack()

    def logout(user_panel):
        user_panel.destroy()
        login(user_type_var.get())

root = tk.Tk()
root.title("Система управления лабораторией")

user_type_var = tk.StringVar(root)
user_type_var.set("администратор")

user_type_label = tk.Label(root, text="Выберите тип пользователя:")
user_type_label.pack()

user_type_menu = ttk.Combobox(root, textvariable=user_type_var, values=("администратор", "бухгалтер", "лаборант", "лаборант-исследователь"))
user_type_menu.pack()

login_button = tk.Button(root, text="Начать вход", command=lambda: login(user_type_var.get()))
login_button.pack()

root.mainloop()

conn.close()