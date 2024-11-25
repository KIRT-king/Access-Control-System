import pickle
import threading
import asyncio

from requests import session
from sqlalchemy.orm import Session

from db.database import Session
from db.models import User, Company
from make_hash import get_sha256_hash
from RSA import decrypt_text_rsa
from elasticsearch_file import log_registration, log_level_change


def run_async_log_registration(login, mac=None):
    asyncio.run(log_registration(login, mac))

def create_new_user(login, password, company, level, ip, mac, location, email, face_id=None, user_status="active"):
    session = Session()
    try:
        new_user = User(
            login=login, password=password, face=face_id, company=company, level=level,
            clas="user", ip=ip, mac=mac, location=location, mail=email, user_status=user_status
        )
        session.add(new_user)
        session.commit()
        threading.Thread(target=run_async_log_registration, args=(login, mac)).start()
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()


def create_new_company(name, password, owner_login, owner_ip, owner_mac, owner_location, number_of_employee):
    session = Session()
    try:
        new_company = Company(
            name_company=name, password_company=password, owner_login=owner_login, owner_ip=owner_ip,
            owner_mac=owner_mac, owner_location=owner_location, number_of_employee=number_of_employee
        )
        session.add(new_company)
        session.commit()
        threading.Thread(target=run_async_log_registration, args=(name,)).start()
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()

def company_check_number_users(name_company):
    session = Session()
    name_company = get_sha256_hash(name_company)
    try:
        info_company = session.query(Company).filter_by(name_company=name_company).first()
        return info_company.number_of_employee
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()

def company_reg_employee(name_company):
    session = Session()
    name_company = get_sha256_hash(name_company)
    try:
        info_company = session.query(Company).filter_by(name_company=name_company).first()
        if info_company and info_company.number_of_employee > 0:
            info_company.number_of_employee -= 1
            session.commit()
        else:
            return "no_place_in_company"
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()


def getdata(login):
    session = Session()
    try:
        user_info = session.query(User).filter_by(login=login).first()
        user_login = user_info.login
        user_password = user_info.password
        user_clas = user_info.clas
        user_level = user_info.level
        user_face = pickle.loads(user_info.face)
        user_email = decrypt_text_rsa(user_info.mail, "admin", "A2D5M2I5N2")
        user_status = user_info.user_status
        return user_login, user_password, user_face, user_clas, user_level, user_email, user_status
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()

def upgrade_user_level(login, level):
    session = Session()
    login = get_sha256_hash(login)
    try:
        user = session.query(User).filter_by(login=login).first()
        if user:
            user.level = level
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
        return False
    finally:
        session.close()

def check_company_and_password(company_login, company_password):
    session = Session()
    company_login = get_sha256_hash(company_login)
    company_password = get_sha256_hash(company_password)
    try:
        result = session.query(Company).filter_by(name_company=company_login).first()
        if not result:
            return "company_not_found"
        if result.password_company != company_password:
            return "invalid_password"
        return "good"
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
        return False
    finally:
        session.close()

def change_company(user_login, company_name):
    session = Session()
    try:
        user_info = session.query(User).filter_by(login=user_login).first()
        user_info.company = company_name
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
        return False
    finally:
        session.close()

def run_async_log_level_change(user_login, old_status, new_status):
    asyncio.run(log_level_change(user_login, old_status, new_status))

def change_status(user_login, status):
    session = Session()
    try:
        user_info = session.query(User).filter_by(login=user_login).first()
        threading.Thread(target=run_async_log_level_change, args=(user_login, user_info.user_status, status)).start()
        user_info.user_status = status
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
        return False
    finally:
        session.close()
