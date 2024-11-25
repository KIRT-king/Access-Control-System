import time
import tkinter as tk
from tkinter import messagebox
from db.commands import getdata, change_status
from make_hash import get_sha256_hash
from regestration.app_pers import open_personal_registration_window
from regestration.app_company import open_company_registration_window
import hmac
import threading
from idlelib.tooltip import Hovertip
from text import user_agreement
from mail import generate_code, send_email, check_code
from RSA import decrypt_text_rsa

incorrect_attempts = 0
max_incorrect_attempts = 5
is_ver_open = False

global user_login, user_password, user_face, user_clas, user_level, user_email, user_status

def App():
    user_data = None

    def GetData():
        nonlocal user_data
        data1 = get_sha256_hash(entry1.get())    # login
        data2 = get_sha256_hash(entry2.get())    # password
        if data1 and data2:
            user_info = getdata(data1)
            if user_info:
                global user_login, user_password, user_face, user_clas, user_level, user_email, user_status
                user_login, user_password, user_face, user_clas, user_level, user_email, user_status = user_info
                if user_status == "disactive":
                    open_verification_window()
                    return
                if hmac.compare_digest(user_password, data2):
                    print("success")
                    user_data = (user_login, user_password, user_face, user_clas, user_level)
                    root.destroy()
                else:
                    show_invalid_login()
            else:
                show_invalid_login()

    def show_invalid_login():
        global incorrect_attempts, user_login
        incorrect_attempts += 1
        entry2.delete(0, tk.END)
        error_label.config(text="Неправильный логин или пароль")

        if incorrect_attempts >= max_incorrect_attempts:
            change_status(user_login, "disactive")
            open_verification_window()

    def on_enter(event=None):
        if not is_ver_open:
            GetData()

    def open_verification_window():
        global is_ver_open, timer_id
        if is_ver_open:
            return
        is_ver_open = True
        verification_window = tk.Toplevel(root)
        verification_window.title("Верификация")
        verification_window.geometry("300x400")
        verification_window.resizable(False, False)
        code_entry = tk.Entry(verification_window, font=("Arial", 20, "bold"), width=10, justify="center", bd=3)
        code_entry.pack(pady=10)
        code_entry.focus_set()

        status_label = tk.Label(verification_window, text="", font=("Arial", 12), fg="red")
        status_label.pack(pady=10)

        timer_label = tk.Label(verification_window, text="00:00", font=("Arial", 14))
        timer_label.pack(pady=5)

        verification_code = generate_code()
        threading.Thread(target=async_send_code, args=(verification_code,)).start()
        start_time = time.time()

        timer_id = None

        def start_timer():
            global timer_id
            time_left = 60 - (time.time() - start_time)
            if time_left <= 0:
                status_label.config(text="Код просрочен", fg="red")
            else:
                minutes = int(time_left // 60)
                seconds = int(time_left % 60)
                timer_label.config(text=f"{minutes:02}:{seconds:02}")
                timer_id = verification_window.after(1000, start_timer)

        def cancel_timer():
            global timer_id
            if timer_id is not None:
                verification_window.after_cancel(timer_id)
                timer_id = None

        def verify_code():
            user_code = code_entry.get()
            if not user_code:
                status_label.config(text="Пароль введен неправильно", fg="red")
                return
            elif len(user_code) != 6:
                status_label.config(text="Неверное количество символов", fg="red")
                return
            else:
                status_label.config(text="")
                if len(user_code) == 6 and check_code(user_code, verification_code, start_time):
                    messagebox.showinfo("Верный код", "Код подтвержден успешно!")
                    change_status(user_login, "active")
                    cancel_timer()
                    verification_window.destroy()
                    global incorrect_attempts, is_ver_open
                    incorrect_attempts = 0
                    is_ver_open = False
                    enable_login_button()
                else:
                    status_label.config(text="Неправильный код", fg="red")

        def resend_code():
            nonlocal start_time, verification_code
            cancel_timer()  # Останавливаем текущий таймер
            verification_code = generate_code()
            threading.Thread(target=async_send_code, args=(verification_code,)).start()
            start_time = time.time()
            status_label.config(text="Код отправлен повторно", fg="blue")
            code_entry.delete(0, tk.END)
            start_timer()  # Запускаем новый таймер

        verify_button = tk.Button(verification_window, text="Подтвердить", font=("Arial", 16), command=verify_code)
        verify_button.pack(pady=20)

        resend_button = tk.Button(verification_window, text="Отправить код повторно", font=("Arial", 12),
                                  command=resend_code)
        resend_button.pack(pady=20)

        start_timer()  # Запуск начального таймера
        disable_login_button()

    def async_send_code(verification_code):
        global user_email
        print(user_email)
        print(decrypt_text_rsa(user_email, get_sha256_hash("admin"), get_sha256_hash("A2D5M2I5N2")))
        send_email(decrypt_text_rsa(user_email, get_sha256_hash("admin"), get_sha256_hash("A2D5M2I5N2")), verification_code)

    def disable_login_button():
        butEnter.config(state=tk.DISABLED)

    def enable_login_button():
        butEnter.config(state=tk.NORMAL)

    def open_registration_choice_window():
        reg_choice_window = tk.Toplevel(root)
        reg_choice_window.title("Выберите тип регистрации")
        reg_choice_window.geometry("500x200")

        def open_personal_registration():
            open_personal_registration_window(root)
            reg_choice_window.destroy()

        def open_company_registration():
            open_company_registration_window(root)
            reg_choice_window.destroy()

        def show_agreements():
            agreement_window = tk.Toplevel(reg_choice_window)
            agreement_window.title("Соглашения")
            agreement_window.geometry("400x400")
            agreement_window.resizable(False, False)

            agreement_text = tk.Text(agreement_window, font=("Arial", 12), wrap="word", height=15, width=40)
            agreement_text.insert(tk.END, user_agreement)
            agreement_text.config(state=tk.DISABLED)

            scrollbar = tk.Scrollbar(agreement_window, orient="vertical", command=agreement_text.yview)
            agreement_text.config(yscrollcommand=scrollbar.set)

            agreement_text.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

        personal_button = tk.Button(reg_choice_window, text="Личная Регистрация", font=("Arial", 20, "bold"), width=19, command=open_personal_registration)
        personal_button.grid(row=0, column=0, padx=(50, 10), pady=(30, 10))

        personal_info_button = tk.Button(reg_choice_window, text="?", font=("Arial", 20, "bold"), command=show_agreements)
        personal_info_button.grid(row=0, column=1, pady=(30, 10))
        Hovertip(personal_info_button, "подсказка", hover_delay=100)

        company_button = tk.Button(reg_choice_window, text="Регистрация Компании", font=("Arial", 20, "bold"), width=19, command=open_company_registration)
        company_button.grid(row=1, column=0, padx=(50, 10), pady=(10, 30))

        company_info_button = tk.Button(reg_choice_window, text="?", font=("Arial", 20, "bold"), command=show_agreements)
        company_info_button.grid(row=1, column=1, pady=(10, 30))
        Hovertip(company_info_button, "подсказка", hover_delay=100)

    # Инициализация окна
    root = tk.Tk()
    root.title("Authentication")
    root.geometry("720x360")
    root.resizable(False, False)

    label = tk.Label(root, text="Идентификатор пользователя:", font=("Arial", 20, "bold"))
    label.place(x=20, y=20)

    entry1 = tk.Entry(root, font=("Arial", 20, "bold"))
    entry1.place(x=450, y=25, width=200, height=30)

    label = tk.Label(root, text="Пароль:", font=("Arial", 20, "bold"))
    label.place(x=20, y=60)

    entry2 = tk.Entry(root, font=("Arial", 20, "bold"), show='*')
    entry2.place(x=450, y=65, width=200, height=30)

    butEnter = tk.Button(root, text="Вход", font=("Arial", 20, "bold"), width=8, height=1, command=GetData)
    butEnter.place(x=360, y=150)

    error_label = tk.Label(root, text="", font=("Arial", 10), fg="red")
    error_label.place(x=450, y=100)

    reg_button = tk.Button(root, text="Регистрация", font=("Arial", 20, "bold"), command=open_registration_choice_window)
    reg_button.place(x=300, y=250)

    root.bind("<Return>", on_enter)
    root.mainloop()

    return user_data
