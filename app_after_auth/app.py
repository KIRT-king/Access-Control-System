import tkinter as tk
from tkinter import messagebox
import os
import subprocess
import win32com.client
from authentication_script.app_auth import App

programs_file = "D:\\Python\\NDTP_2\\program\\programs.txt"
program_folder = "D:\\Python\\NDTP_2\\program"

def read_programs(file_path):
    programs = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                parts = line.strip().rsplit(" ", 1)
                if len(parts) == 2:
                    program_name = parts[0]
                    try:
                        access_level = int(parts[1])
                        programs.append((program_name, access_level))
                    except ValueError:
                        print(f"Ошибка: некорректный уровень доступа в строке: {line}")
                else:
                    print(f"Ошибка в формате строки: {line}")
    except FileNotFoundError:
        print(f"Ошибка: файл {file_path} не найден.")
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
    return programs


def delete_user():
    print("Удаление учетной записи...")
    App()

def run_program(program_name):
    try:
        program_path = os.path.join(program_folder, f"{program_name}.lnk")
        if os.path.isfile(program_path):
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortcut(program_path)
            subprocess.run(shortcut.TargetPath, check=True)
        else:
            program_path = os.path.join(program_folder, f"{program_name}.exe")
            if os.path.isfile(program_path):
                subprocess.run(program_path, check=True)
            else:
                raise FileNotFoundError(f"Программа {program_name} не найдена.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось запустить программу: {e}")

def show_programs(user_level):
    programs = read_programs(programs_file)

    if not programs:
        print("Нет доступных программ для отображения.")
        return

    app = tk.Tk()
    app.title("Доступные программы")
    app.geometry("1200x675")
    app.resizable(False, False)
    app.configure(bg='#FBEEC1')

    header_frame = tk.Frame(app, bg='#BC986A', height=80, width=1200)
    header_frame.pack(fill="x", side="top", pady=0)

    title_label = tk.Label(header_frame, text="Доступные приложения для вашего уровня:", font=("Arial", 24, "bold"), bg='#BC986A', fg="white")
    title_label.pack(pady=20)

    def exit_program():
        app.destroy()
        App()

    def confirm_delete_user():
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить учетную запись?"):
            delete_user()
            app.destroy()
            App()

    exit_button = tk.Button(header_frame, text="В - Выход", font=("Arial", 16, "bold"), command=exit_program, relief="flat", bg='#BC986A', fg="white")
    exit_button.pack(side="right", padx=10)

    delete_button = tk.Button(header_frame, text="У - Удалить", font=("Arial", 16, "bold"), command=confirm_delete_user, relief="flat", bg='#BC986A', fg="white")
    delete_button.pack(side="right", padx=10)

    program_frame = tk.Frame(app, bg='#FBEEC1')
    program_frame.pack(pady=20, padx=20, fill='both', expand=True)

    program_canvas = tk.Canvas(program_frame, bg='#FBEEC1', bd=0, highlightthickness=0)
    program_canvas.pack(side="left", fill="both", expand=True)

    program_list_frame = tk.Frame(program_canvas, bg='#FBEEC1')
    program_canvas.create_window((0, 0), window=program_list_frame, anchor="nw")

    program_list_frame.bind("<Configure>", lambda e: program_canvas.configure(scrollregion=program_canvas.bbox("all")))

    def on_mouse_wheel(event):
        program_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    program_canvas.bind_all("<MouseWheel>", on_mouse_wheel)

    font_style = ("Arial", 18, "bold")

    row = 0
    for program_name, access_level in programs:
        if user_level >= access_level:
            program_button = tk.Button(program_list_frame, text=program_name, font=font_style, anchor="w", bg="#DAAD86", fg="black", width=50, height=3, relief="solid", bd=0, padx=10, pady=5)
            program_button.grid(row=row, column=0, pady=5, sticky="w")

            program_path = os.path.join(program_folder, f"{program_name}.lnk")
            if not os.path.exists(program_path):
                program_path = os.path.join(program_folder, f"{program_name}.exe")

            program_button.config(command=lambda p=program_name: run_program(p))

            row += 1

    app.mainloop()
