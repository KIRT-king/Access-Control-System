import re

def check_password_strength(password):
    if len(password) < 10:
        return "Invalid_len"

    if re.search(r'[а-яА-Я]', password):
        return "Password_contains_russian_letters"

    if not re.search(r'\d', password):
        return "Invalid_number_of_digit"

    if not re.search(r'[A-Z]', password):
        return "Invalid_number_of_upcase_letters"

    if not re.search(r'[a-z]', password):
        return "Invalid_number_of_low_letters"

    if not re.search(r'[\W_]', password):
        return "Invalid_number_of_specific_chars"

    return True

def check_login(login):
    if len(login) < 8:
        return "Invalid_len"
    if re.search(r'[а-яА-Я]', login):
        return "Login_contains_russian_letters"