import tkinter as tk
import cv2
import numpy as np
from PIL import Image, ImageTk
import threading
from tkinter import messagebox

from anaconda_cloud_auth import login

from regestration.commands_req import register_request, create_request
from make_hash import get_sha256_hash
from regestration.EncodeGenerator import Encode
from db.commands import check_company_and_password, create_new_user, company_check_number_users, company_reg_employee
from regestration.network_data import get_mac, get_external_ip, get_location
from check_format_of_email import check_email_format
from check_password_and_login import check_login, check_password_strength
from RSA import encrypt_text_rsa, encrypt_text_aes
from elasticsearch_file import log_registration

global login_r, password_r, company_login_r, company_password_r, email_r
global selected_photo


def capture_photos(reg_window, reg_biometry_button, success_label, submit_button):
    CAMERA_ID = 0
    cap = cv2.VideoCapture(CAMERA_ID)
    photos = []

    def capture_single_photo():
        global selected_photo
        ret, frame = cap.read()
        if ret:
            photos.append(frame)
            if len(photos) == 3:
                capture_window.destroy()
                selected_photo = show_photo_selection(reg_window, photos)
                if selected_photo is not None:
                    reg_biometry_button.pack_forget()
                    success_label.pack(pady=(10, 5))
                    submit_button.config(state="normal")

    def update_frame():
        if len(photos) < 3:
            ret, frame = cap.read()
            if ret:
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                video_label.imgtk = imgtk
                video_label.configure(image=imgtk)
            video_label.after(10, update_frame)

    capture_window = tk.Toplevel(reg_window)
    capture_window.title("Сделайте фотографии")
    capture_window.geometry("800x600")
    capture_window.resizable(False, False)
    video_label = tk.Label(capture_window)
    video_label.pack()
    capture_button = tk.Button(capture_window, text="Сделать фото", font=("Arial", 14), command=capture_single_photo)
    capture_button.pack(pady=20)
    update_frame()


def show_photo_selection(reg_window, photos):
    select_window = tk.Toplevel(reg_window)
    select_window.title("Выберите фотографию(предлагаем сделать 3 фотографии)")
    select_window.geometry("1000x400")
    select_window.resizable(False, False)

    chosen_photo = tk.StringVar(value=None)

    def select_photo(index):
        chosen_photo.set(index)
        select_window.destroy()

    for idx, photo in enumerate(photos):
        rgb_photo = cv2.cvtColor(photo, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_photo)
        imgtk = ImageTk.PhotoImage(image=img.resize((300, 200)))

        photo_label = tk.Label(select_window, image=imgtk)
        photo_label.image = imgtk
        photo_label.grid(row=0, column=idx, padx=10)

        select_button = tk.Button(select_window, text=f"Выбрать фото {idx + 1}", command=lambda i=idx: select_photo(i))
        select_button.grid(row=1, column=idx, pady=10)

    select_window.wait_window()

    if chosen_photo.get() is not None:
        selected_index = int(chosen_photo.get())
        return photos[selected_index]
    else:
        return None


def open_personal_registration_window(root):
    reg_window = tk.Toplevel(root)
    reg_window.title("Регистрация(лич)")
    reg_window.geometry("500x950")
    reg_window.resizable(False, False)

    reg_label = tk.Label(reg_window, text="Регистрация", font=("Arial", 20, "bold"))
    reg_label.pack(pady=5)

    reg_login_label = tk.Label(reg_window, text="Логин:", font=("Arial", 20, "bold"))
    reg_login_label.pack(pady=5)
    reg_login_entry = tk.Entry(reg_window, font=("Arial", 20, "bold"))
    reg_login_entry.pack(pady=5, ipady=5)

    login_error_label = tk.Label(reg_window, text="", font=("Arial", 10), fg="red")
    login_error_label.pack()

    reg_password_label = tk.Label(reg_window, text="Пароль:", font=("Arial", 20, "bold"))
    reg_password_label.pack(pady=10)
    reg_password_entry = tk.Entry(reg_window, font=("Arial", 20, "bold"), show='*')
    reg_password_entry.pack(pady=(0, 5), ipady=5)

    check_password_label = tk.Label(reg_window, text="Повторите пароль:", font=("Arial", 20, "bold"))
    check_password_label.pack(pady=10)
    check_password_entry = tk.Entry(reg_window, font=("Arial", 20, "bold"), show='*')
    check_password_entry.pack(pady=(0, 5), ipady=5)

    password_error_label = tk.Label(reg_window, text="", font=("Arial", 10), fg="red")
    password_error_label.pack()

    reg_email_label = tk.Label(reg_window, text="Электронная почта:", font=("Arial", 20, "bold"))
    reg_email_label.pack(pady=5)
    reg_email_entry = tk.Text(reg_window, width=25, height=1.45, font=("Arial", 16, "bold"))
    reg_email_entry.pack(pady=5, ipady=5)

    email_error_label = tk.Label(reg_window, text="", font=("Arial", 10), fg="red")
    email_error_label.pack()

    reg_company_label = tk.Label(reg_window, text="Ваша компания:", font=("Arial", 20, "bold"))
    reg_company_label.pack(pady=10)
    reg_company_entry = tk.Entry(reg_window, font=("Arial", 20, "bold"))
    reg_company_entry.insert(0, "solo")
    reg_company_entry.pack(pady=(0, 5), ipady=5)

    company_error_label = tk.Label(reg_window, text="", font=("Arial", 10), fg="red")
    company_error_label.pack()

    password_company_label = tk.Label(reg_window, text="Пароль компании(можно оставить пустым):", font=("Arial", 13, "bold"))
    password_company_label.pack(pady=10)
    password_company_entry = tk.Entry(reg_window, font=("Arial", 20, "bold"), show='*')
    password_company_entry.pack(pady=(0, 5), ipady=5)

    def validate_fields():
        empty_fields = False
        login_error_label.config(text="")
        password_error_label.config(text="")
        company_error_label.config(text="")
        email_error_label.config(text="")

        global login_r, password_r, company_login_r, company_password_r, email_r
        login_r = reg_login_entry.get()
        password_r = reg_password_entry.get()
        company_login_r = reg_company_entry.get()
        company_password_r = password_company_entry.get()
        email_r = reg_email_entry.get("1.0", "end-1c")

        for label in [reg_login_label, reg_password_label, check_password_label, reg_company_label, reg_email_label]:
            label.config(fg="black")

        if not login_r:
            reg_login_label.config(fg="red")
            empty_fields = True
        if not password_r:
            reg_password_label.config(fg="red")
            empty_fields = True
        if not check_password_entry.get():
            check_password_label.config(fg="red")
            empty_fields = True
        if not email_r:
            reg_email_label.config(fg="red")
            empty_fields = True
        if not company_login_r:
            reg_company_label.config(fg="red")
            empty_fields = True
        answer_request = register_request(login_r, get_mac())
        if not empty_fields and answer_request[0] == "Invalid_login":
            login_error_label.config(text="Логин уже занят")
            return
        if login_r != "admin":
            res_login = check_login(login_r)
            if res_login == "Invalid_len":
                login_error_label.config(text="Логин должен содержать не менее 8 символов")
                return
            elif res_login == "Login_contains_russian_letters":
                login_error_label.config(text="Логин не должен содержать русские буквы")
                return

            res_password = check_password_strength(password_r)
            if res_password == "Invalid_len":
                password_error_label.config(text="Пароль должен содержать не менее 10 символов")
                return
            elif res_password == "Password_contains_russian_letters":
                password_error_label.config(text="Пароль не должен содержать русские буквы")
                return
            elif res_password == "Invalid_number_of_digit":
                password_error_label.config(text="Пароль должен содержать хотя бы одну цифру")
                return
            elif res_password == "Invalid_number_of_upcase_letters":
                password_error_label.config(text="Пароль должен содержать хотя бы одну заглавную букву")
                return
            elif res_password == "Invalid_number_of_low_letters":
                password_error_label.config(text="Пароль должен содержать хотя бы одну строчную букву")
                return
            elif res_password == "Invalid_number_of_specific_chars":
                password_error_label.config(text="Пароль должен содержать хотя бы один специальный символ")
                return

        if password_r != check_password_entry.get():
            password_error_label.config(text="Пароли не совпадают")
            return

        if company_login_r == "solo" and answer_request[1] == "Invalid_mac":
            messagebox.showerror("Ошибка MAC", "Вы уже зарегистрированы")
            return

        res_check_email_format = check_email_format(email_r)
        if res_check_email_format == "no_dog_char":
            email_error_label.config(text="Неправильный формат электронной почты")
            return
        elif res_check_email_format == "involid_domen":
            email_error_label.config(text="Неизвестный домен эклектронной почтв")
            return

        if company_login_r != "solo":
            result = check_company_and_password(company_login_r, company_password_r)
            result_employee = company_check_number_users(company_login_r)
            if result == "company_not_found":
                reg_company_entry.delete(0, tk.END)
                reg_company_entry.insert(0, "solo")
                reg_company_label.config(fg="red")
                company_error_label.config(text="Компания не найдена")
                return

            if result == "invalid_password":
                password_company_entry.delete(0, tk.END)
                password_company_entry.insert(0, "")
                password_company_label.config(fg="red")
                company_error_label.config(text="Неверный пароль для компании")
                return

            if result_employee == 0:
                messagebox.showerror("Переполнение", "Нет мест внутри компании\nСвяжитесь с сис. администратором")
                return

            if result == "good":
                password_company_label.config(fg="black")

        if not empty_fields:
            threading.Thread(target=capture_photos, args=(reg_window, reg_biometry_button, success_label, submit_button)).start()

    reg_biometry_button = tk.Button(reg_window, text="Внести биометрию", font=("Arial", 20, "bold"), width=19, command=validate_fields)
    reg_biometry_button.pack(pady=(10, 5))

    success_label = tk.Label(reg_window, text="Биометрия введена успешно", font=("Arial", 20, "bold"), fg="green")

    def success_reg_pers():
        global selected_photo, login_r, password_r, company_login_r, email_r
        img = Image.fromarray(selected_photo)
        resize_img = img.resize((216, 216), Image.Resampling.LANCZOS)
        resize_img_np = np.array(resize_img)
        x = Encode(resize_img_np)
        if x:
            if company_login_r == "solo":
                create_request(login_r,
                               password_r,
                               x,
                               company_login_r,
                               email_r)
                tk.messagebox.showinfo("Успех", "Заявка подана!")
            elif company_login_r != "solo":
                login_r = get_sha256_hash(login_r)
                password_r = get_sha256_hash(password_r)
                ip = encrypt_text_rsa(get_external_ip())
                mac = encrypt_text_aes(get_mac())
                location = encrypt_text_rsa(get_location(ip))
                email = encrypt_text_rsa(email_r)
                create_new_user(login_r, password_r, company_login_r, 1,
                                ip, mac, location, email, x)
                company_reg_employee(company_login_r)
                tk.messagebox.showinfo("Успех", "Вы зарегистрированы")
        else:
            tk.messagebox.showwarning("Ошибка", "Фото не выбрано или была выбрана плохая фотография.\nЗаявка не подана!")
        reg_window.destroy()

    submit_button = tk.Button(reg_window, text="Подать заявку", font=("Arial", 20, "bold"), width=19, state="disabled", command=success_reg_pers)
    submit_button.pack(pady=(10, 5))

