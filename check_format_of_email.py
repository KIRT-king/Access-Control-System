from email_domens import email_domains

def check_email_format(email):
    if "@" not in email:
        return "no_dog_char"
    local_part, domain = email.split("@", 1)

    if domain not in email_domains:
        return "involid_domen"
    return "success"