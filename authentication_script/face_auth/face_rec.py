import os
import cv2
import cvzone
import numpy as np
import face_recognition
import threading
import tkinter as tk
import asyncio
from ultralytics import YOLO

from authentication_script.app_auth import App
from app_after_auth.app import show_programs
from admin.admin_main import open_admin_panel
from elasticsearch_file import log_login

# const and path
PATH_IMG_BACKGROUND = "Resources\\background.png"
PATH_IMG_MODES = "Resources\\Modes"
modeType = 0
counter = 0
CAMERA_ID = 0
BLOCK_TIME = 20  # Время блокировки (в секундах)

modePathList = os.listdir(PATH_IMG_MODES)
imgModeList = [cv2.imread(os.path.join(PATH_IMG_MODES, path)) for path in modePathList]

cap = cv2.VideoCapture(CAMERA_ID)
cap.set(3, 640)
cap.set(4, 480)
imgBackground = cv2.imread(PATH_IMG_BACKGROUND)

resault = App()
user_login = resault[0]
user_password = resault[1]
user_face = resault[2]
user_clas = resault[3]
user_level = resault[4]
flag_off = False
is_blocked = False  # Флаг блокировки
block_start_time = None  # Время начала блокировки
# Загружаем модель YOLO

phone_detector = YOLO("../../yolov9m.pt")


# print(user_face)
if resault:
    async def async_log_login():
        await log_login(user_login)

    def create_choice_window():
        def open_main_app():
            show_programs(user_level)

        def open_admin():
            open_admin_panel(user_login, user_password)

        def exit_program():
            choice_app.destroy()
            App()

        choice_app = tk.Tk()
        choice_app.title("Выбор приложения")
        choice_app.geometry("800x400")
        choice_app.resizable(False, False)

        label = tk.Label(choice_app, text="Выберите приложение", font=("Arial", 24, "bold"))
        label.pack(pady=10)

        admin_button = tk.Button(choice_app, text="Панель администратора", font=("Arial", 24, "bold"), width=25,
                                 command=open_admin)
        admin_button.pack(pady=5)

        app_button = tk.Button(choice_app, text="Основное приложение", font=("Arial", 24, "bold"), width=25,
                               command=open_main_app)
        app_button.pack(pady=5)

        exit_button = tk.Button(choice_app, text="Выход", font=("Arial", 24, "bold"), width=25, command=exit_program)
        exit_button.pack(pady=5)

        choice_app.mainloop()

    async def detect_phone(frame):
        global is_blocked, block_start_time, modeType
        results = phone_detector(frame, stream=True)
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                if phone_detector.names[class_id] == "cell phone":
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, "Phone Detected", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    # Активация блокировки
                    if not is_blocked:
                        is_blocked = True
                        block_start_time = cv2.getTickCount() / cv2.getTickFrequency()
                        modeType = 3  # Включение режима блокировки

    while True:
        _, img = cap.read()
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        imgBackground[162:162 + 480, 55:55 + 640] = img
        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

        if is_blocked:
            elapsed_time = cv2.getTickCount() / cv2.getTickFrequency() - block_start_time
            remaining_time = int(BLOCK_TIME - elapsed_time)

            if remaining_time <= 0:
                cv2.rectangle(imgBackground, (10, 10), (150, 60), (255, 255, 255), -1)
                is_blocked = False
                modeType = 0
            else:
                cv2.rectangle(imgBackground, (10, 10), (150, 60), (255, 255, 255), -1)

                cv2.putText(
                    imgBackground,
                    f"{remaining_time}s",
                    (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 0),
                    2
                )

                cv2.imshow("Authentication", imgBackground)
                if cv2.waitKey(1) == ord("q"):
                    break
                continue

        faceCurFrame = face_recognition.face_locations(imgS)
        encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

        if faceCurFrame:
            for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                matches = face_recognition.compare_faces([user_face], encodeFace)
                faceDis = face_recognition.face_distance([user_face], encodeFace)
                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                    imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                    if counter == 0:
                        cvzone.putTextRect(imgBackground, "Loading...", (275, 400))
                        cv2.imshow("Authentication", imgBackground)
                        cv2.waitKey(1)
                        counter = 1
                        modeType = 2

            if counter != 0:
                if 8 < counter < 20:
                    user_level = 1
                    flag_off = True

                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                counter += 1

                if counter >= 20:
                    counter = 0
                    modeType = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
        else:
            modeType = 0
            counter = 0

        asyncio.run(detect_phone(img))

        if flag_off:
            break

        cv2.imshow("Authentication", imgBackground)
        if cv2.waitKey(1) == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    def run_async_log_login():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(async_log_login())
        loop.close()

    threading.Thread(target=run_async_log_login).start()

    if user_clas == "admin":
        create_choice_window()
    else:
        show_programs(user_level)
