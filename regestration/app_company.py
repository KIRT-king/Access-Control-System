import tkinter as tk
from tkinter import messagebox
from regestration.commands_req import company_reg
from check_password_and_login import check_login, check_password_strength

def open_company_registration_window(root):
    reg_window = tk.Toplevel(root)
    reg_window.title("Регистрация(ком)")
    reg_window.geometry("500x800")
    reg_window.resizable(False, False)

    reg_label = tk.Label(reg_window, text="Регистрация Компании", font=("Arial", 20, "bold"))
    reg_label.pack(pady=10)

    company_name_label = tk.Label(reg_window, text="Название компании:", font=("Arial", 20, "bold"))
    company_name_label.pack(pady=10)
    company_name_entry = tk.Entry(reg_window, font=("Arial", 20, "bold"))
    company_name_entry.pack(pady=5, ipady=5)
    company_name_error_label = tk.Label(reg_window, text="", font=("Arial", 12), fg="red")
    company_name_error_label.pack()

    company_password_label = tk.Label(reg_window, text="Пароль компании:", font=("Arial", 20, "bold"))
    company_password_label.pack(pady=(5, 10))
    company_password_entry = tk.Entry(reg_window, font=("Arial", 20, "bold"), show='*')
    company_password_entry.pack(pady=5, ipady=5)
    company_password_error_label = tk.Label(reg_window, text="", font=("Arial", 12), fg="red")
    company_password_error_label.pack()


    admin_login_label = tk.Label(reg_window, text="Логин (Сис. Админ):", font=("Arial", 20, "bold"))
    admin_login_label.pack(pady=10)
    admin_login_entry = tk.Entry(reg_window, font=("Arial", 20, "bold"))
    admin_login_entry.pack(pady=5, ipady=5)
    admin_login_error_label = tk.Label(reg_window, text="", font=("Arial", 12), fg="red")
    admin_login_error_label.pack()

    admin_password_label = tk.Label(reg_window, text="Пароль (Сис. Админ):", font=("Arial", 20, "bold"))
    admin_password_label.pack(pady=10)
    admin_password_entry = tk.Entry(reg_window, font=("Arial", 20, "bold"), show='*')
    admin_password_entry.pack(pady=5, ipady=5)
    admin_password_error_label = tk.Label(reg_window, text="", font=("Arial", 12), fg="red")
    admin_password_error_label.pack()

    employees_label = tk.Label(reg_window, text="Количество участников(2-50):", font=("Arial", 20, "bold"))
    employees_label.pack(pady=10)
    employees_frame = tk.Frame(reg_window)
    employees_frame.pack(pady=5)
    employees_entry = tk.Entry(employees_frame, font=("Arial", 20, "bold"), width=5)
    employees_entry.pack(side=tk.LEFT)
    employees_error_label = tk.Label(reg_window, text="", font=("Arial", 12), fg="red")
    employees_error_label.pack()

    def regestr_company():
        name_company_r = company_name_entry.get()
        company_password_r = company_password_entry.get()
        admin_login = admin_login_entry.get()
        admin_password = admin_password_entry.get()
        number_of_employees = employees_entry.get()

        company_name_error_label.config(text="")
        company_password_error_label.config(text="")
        admin_login_error_label.config(text="")
        admin_password_error_label.config(text="")
        employees_error_label.config(text="")

        res_login = check_login(name_company_r)
        if res_login == "Invalid_len":
            company_name_error_label.config(text="Логин должен содержать не менее 8 символов")
            return
        elif res_login == "Login_contains_russian_letters":
            company_name_error_label.config(text="Логин не должен содержать русские буквы")
            return

        res_password = check_password_strength(company_password_r)
        if res_password == "Invalid_len":
            company_password_error_label.config(text="Пароль должен содержать не менее 10 символов")
            return
        elif res_password == "Password_contains_russian_letters":
            company_password_error_label.config(text="Пароль не должен содержать русские буквы")
            return
        elif res_password == "Invalid_number_of_digit":
            company_password_error_label.config(text="Пароль должен содержать хотя бы одну цифру")
            return
        elif res_password == "Invalid_number_of_upcase_letters":
            company_password_error_label.config(text="Пароль должен содержать хотя бы одну заглавную букву")
            return
        elif res_password == "Invalid_number_of_low_letters":
            company_password_error_label.config(text="Пароль должен содержать хотя бы одну строчную букву")
            return
        elif res_password == "Invalid_number_of_specific_chars":
            company_password_error_label.config(text="Пароль должен содержать хотя бы один специальный символ")
            return

        try:
            number_of_employees = int(number_of_employees)
            if not (2 <= number_of_employees <= 50):
                employees_error_label.config(text="Количество участников должно быть от 2 до 50")
                return
        except ValueError:
            employees_error_label.config(text="Введите числовое значение")
            return

        result = company_reg(name_company_r, company_password_r, admin_login, admin_password, number_of_employees)

        if result == "company_exists":
            company_name_error_label.config(text="Недопустимое или занятое имя компании")
        elif result == "user_not_found":
            admin_login_error_label.config(text="Такого пользователя нет в базе")
        elif result == "wrong_password":
            admin_password_error_label.config(text="Неверный пароль")
        else:
            tk.messagebox.showinfo("Успех", "Заявка на регистрацию подана!")
            reg_window.destroy()

    submit_button = tk.Button(reg_window, text="Подать заявку", font=("Arial", 16, "bold"), width=30, height=1, command=regestr_company)
    submit_button.pack(pady=5)
