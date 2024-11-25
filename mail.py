import smtplib
import random
import string
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
SENDER_EMAIL = 'kirtorganization@gmail.com'
SENDER_PASSWORD = 'hqgh hhyt tubs ixuu'

def generate_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

def send_email(RECEIVER_EMAIL, code):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = 'Ваш код для верификации'

    body = f'Ваш код для верификации: {code}'
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, text)
        server.quit()
        print(f'Код отправлен на email {RECEIVER_EMAIL}')
    except Exception as e:
        print(f'Ошибка отправки email: {e}')

def check_code(user_code, sent_code, sent_time):
    if sent_time and time.time() - sent_time <= 60:
        return user_code == sent_code
    return False
