import tkinter as tk
import os
from tkinter import ttk, messagebox

from regestration.commands_req import get_10_requests_users, remove_user_request_from_db, get_10_requests_companies, remove_company_request_from_db
from db.commands import create_new_user, create_new_company, change_company
from make_hash import get_sha256_hash
from dotenv import load_dotenv, find_dotenv
from db.commands import upgrade_user_level, change_company, company_reg_employee
from RSA import decrypt_text_rsa, decrypt_text_aes

load_dotenv(find_dotenv())
global users_from_db, companies_from_db, user_login, user_password

def accept_user_request(tree):
    global users_from_db
    selected_item = tree.selection()
    if selected_item:
        item_values = tree.item(selected_item, 'values')
        login = item_values[0]

        user_to_add = None
        for user in users_from_db:
            if user.login_r == login:
                user_to_add = user
                break

        if user_to_add:
            create_new_user(user_to_add.login_r, user_to_add.password_r, user_to_add.company_r,
                            1, user_to_add.ip_r,  user_to_add.mac_r, user_to_add.location_r,
                            user_to_add.mail_r, user_to_add.face_r)
            remove_user_request_from_db(user_to_add.login_r)
            tree.delete(selected_item)
            messagebox.showinfo("Принять запрос", f"Запрос от {login} принят и добавлен в базу данных!")
        else:
            messagebox.showwarning("Ошибка", "Пользователь не найден в списке заявок!")
    else:
        messagebox.showwarning("Выбор", "Выберите запрос для принятия!")

def accept_company_request(tree):
    global companies_from_db
    selected_item = tree.selection()
    if selected_item:
        item_values = tree.item(selected_item, 'values')
        company_name = item_values[0]

        company_to_add = None
        for company in companies_from_db:
            if company.name_company_r == company_name:
                company_to_add = company
                break

        if company_to_add:
            create_new_company(company_to_add.name_company_r, company_to_add.password_company_r, company_to_add.owner_login_r, company_to_add.owner_ip_r,
                               company_to_add.owner_mac_r, company_to_add.owner_location_r, company_to_add.number_of_employee_r)
            remove_company_request_from_db(company_to_add.name_company_r)
            change_company(company_to_add.owner_login_r, company_to_add.name_company_r)
            company_reg_employee(company_to_add.name_company_r)
            tree.delete(selected_item)
            messagebox.showinfo("Принять запрос", f"Запрос от {company_to_add.name_company_r} принят и добавлен в базу данных!")
        else:
            messagebox.showwarning("Ошибка", "Компания не найдена в списке заявок!")
    else:
        messagebox.showwarning("Выбор", "Выберите запрос для принятия!")

def reject_user_request(tree):
    selected_item = tree.selection()
    if selected_item:
        item_values = tree.item(selected_item, 'values')
        login = item_values[0]

        user_to_add = None
        for user in users_from_db:
            if user.login_r == login:
                user_to_add = user
                break
        remove_user_request_from_db(user_to_add.login_r)
        tree.delete(selected_item)
        messagebox.showinfo("Отклонить запрос", f"Запрос от {login} отклонён!")
    else:
        messagebox.showwarning("Выбор", "Выберите запрос для отклонения!")

def reject_company_request(tree):
    selected_item = tree.selection()
    if selected_item:
        item_values = tree.item(selected_item, 'values')
        company_name = item_values[0]

        company_to_add = None
        for company in companies_from_db:
            if company.name_company_r == company_name:
                company_to_add = company
                break
        remove_company_request_from_db(company_to_add.name_company_r)
        tree.delete(selected_item)
        messagebox.showinfo("Отклонить запрос", f"Запрос от {company_to_add.name_company_r} отклонён!")
    else:
        messagebox.showwarning("Выбор", "Выберите запрос для отклонения!")

def show_user_data(tree):
    global users_from_db
    users_from_db = get_10_requests_users()
    for row in tree.get_children():
        tree.delete(row)
    if users_from_db:
        for user in users_from_db:
            tree.insert("", "end", values=(user.login_r, decrypt_text_rsa(user.ip_r, user_login, user_password),
                                                         decrypt_text_aes(user.mac_r),
                                                         decrypt_text_rsa(user.location_r, user_login, user_password)))
    else:
        messagebox.showinfo("Нет данных", "Нет доступных запросов для отображения.")

def show_company_requests(tree):
    global companies_from_db
    companies_from_db = get_10_requests_companies()
    for row in tree.get_children():
        tree.delete(row)
    if companies_from_db:
        for company in companies_from_db:
            tree.insert("", "end", values=(company.name_company_r, company.owner_login_r,
                                           decrypt_text_rsa(company.owner_ip_r, user_login, user_password),
                                           decrypt_text_aes(company.owner_mac_r),
                                           decrypt_text_rsa(company.owner_location_r, user_login, user_password)))
    else:
        messagebox.showinfo("Нет данных", "Нет доступных запросов для отображения.")


def open_admin_panel(login, password):
    global user_login, user_password
    user_login = login
    user_password = password
    admin_panel = tk.Tk()
    admin_panel.title("Административная панель")
    admin_panel.resizable(False, False)
    font_style = ("Arial", 20, "bold")

    tab_control = ttk.Notebook(admin_panel)

    tab1 = ttk.Frame(tab_control)
    tab_control.add(tab1, text="Просмотр пользователей")

    tree = ttk.Treeview(tab1, columns=("login", "ip", "mac", "location"), show="headings")
    tree.heading("login", text="Логин")
    tree.heading("ip", text="IP")
    tree.heading("mac", text="MAC")
    tree.heading("location", text="Локация")

    tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    show_user_data_button = tk.Button(tab1, text="Показать запросы", font=font_style,
                                      command=lambda: show_user_data(tree))
    show_user_data_button.pack(pady=10)

    def show_context_menu_users(event):
        try:
            tree.selection_set(tree.identify_row(event.y))
        except IndexError:
            pass
        context_menu.post(event.x_root, event.y_root)

    context_menu = tk.Menu(admin_panel, tearoff=0)
    context_menu.add_command(label="Принять запрос", command=lambda: accept_user_request(tree))
    context_menu.add_command(label="Отклонить запрос", command=lambda: reject_user_request(tree))

    tree.bind("<Button-3>", show_context_menu_users)

    tab_company_requests = ttk.Frame(tab_control)
    tab_control.add(tab_company_requests, text="Заявки компаний")

    company_tree = ttk.Treeview(tab_company_requests, columns=("company_name", "login", "ip", "mac", "location"),
                                show="headings")
    company_tree.heading("company_name", text="Компания")
    company_tree.heading("login", text="Логин")
    company_tree.heading("ip", text="IP")
    company_tree.heading("mac", text="MAC")
    company_tree.heading("location", text="Локация")

    company_tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    show_company_data_button = tk.Button(tab_company_requests, text="Показать заявки компаний", font=font_style,
                                         command=lambda: show_company_requests(company_tree))
    show_company_data_button.pack(pady=10)

    def show_context_menu_companies(event):
        try:
            selected_item = company_tree.identify_row(event.y)
            if selected_item:
                company_tree.selection_set(selected_item)
                context_menu_companies.post(event.x_root, event.y_root)
            else:
                print("Не выбран элемент для компании.")
        except IndexError:
            pass

    context_menu_companies = tk.Menu(admin_panel, tearoff=0)
    context_menu_companies.add_command(label="Принять запрос", command=lambda: accept_company_request(company_tree))
    context_menu_companies.add_command(label="Отклонить запрос", command=lambda: reject_company_request(company_tree))
    company_tree.bind("<Button-3>", show_context_menu_companies)

    tab2 = ttk.Frame(tab_control)
    tab_control.add(tab2, text="Повышение уровня")

    label_login = tk.Label(tab2, text="Логин пользователя:", font=font_style)
    label_login.grid(row=0, column=0, padx=10, pady=10)
    entry_login = tk.Entry(tab2, font=font_style)
    entry_login.grid(row=0, column=1, padx=10, pady=10)

    label_password = tk.Label(tab2, text="Пароль администратора:", font=font_style)
    label_password.grid(row=1, column=0, padx=10, pady=10)
    entry_password = tk.Entry(tab2, show="*", font=font_style)
    entry_password.grid(row=1, column=1, padx=10, pady=10)

    level_text = tk.Text(tab2, width= 5, height=10)
    label_level = tk.Label(tab2, text="Новый уровень(1-100):", font=font_style)
    label_level.grid(row=2, column=0, padx=10, pady=10)
    entry_level = tk.Entry(tab2, font=font_style)
    entry_level.grid(row=2, column=1, padx=10, pady=10)

    def on_upgrade_button_click():
        login = entry_login.get()
        password = entry_password.get()

        # Проверяем, является ли введённый пароль корректным
        if get_sha256_hash(password) != os.getenv("ADMIN_PASSWORD"):
            messagebox.showerror("Ошибка", "Неверный пароль администратора!")
            return

        try:
            new_level = int(entry_level.get())
            if 1 <= new_level <= 100:
                if upgrade_user_level(login, new_level):
                    messagebox.showinfo("Успех", f"Уровень пользователя - {login} изменён на - {new_level}")
                    entry_login.delete(0, tk.END)
                    entry_password.delete(0, tk.END)
                    entry_level.delete(0, tk.END)
                else:
                    messagebox.showerror("Ошибка", f"Пользователь с логином {login} не найден.")
            else:
                messagebox.showerror("Ошибка", "Уровень должен быть от 1 до 100!")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректный уровень (число от 1 до 100)!")

    upgrade_button = tk.Button(tab2, text="Изменить уровень", font=font_style, command=on_upgrade_button_click)
    upgrade_button.grid(row=3, columnspan=2, pady=20)

    tab_control.pack(expand=1, fill="both")
    admin_panel.mainloop()
