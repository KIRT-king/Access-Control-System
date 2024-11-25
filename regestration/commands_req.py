from regestration.database_req import Session_r
from regestration.models_req import User_r, Company_r
from db.database import Session
from db.models import User, Company
from regestration.network_data import get_mac, get_location, get_external_ip
from make_hash import get_sha256_hash
from RSA import encrypt_text_rsa, encrypt_text_aes


def register_request(login: str, mac):
    login = get_sha256_hash(login)
    mac = encrypt_text_aes(mac)
    session = Session()
    session_r = Session_r()

    user = session.query(User).filter_by(login=login).first()
    user_r = session_r.query(User_r).filter_by(login_r=login).first()

    find_mac = session.query(User).filter_by(mac=mac).first()
    find_mac_r = session_r.query(User_r).filter_by(mac_r=mac).first()

    error_list = []

    if user or user_r:
        session.close()
        session_r.close()
        error_list.append("Invalid_login")
    else:
        error_list.append("Normal_login")

    if find_mac or find_mac_r:
        session.close()
        session_r.close()
        error_list.append("Invalid_mac")
    else:
        error_list.append("Normal_mac")


    session.close()
    session_r.close()
    return error_list

def create_request(login, password, face_id, company, email):
    session_r = Session_r()
    try:
        ip = get_external_ip()
        mac = get_mac()
        location = get_location(ip)
        ip = encrypt_text_rsa(ip)
        mac = encrypt_text_aes(mac)
        location = encrypt_text_rsa(location)
        email = encrypt_text_rsa(email)

        login = get_sha256_hash(login)
        password = get_sha256_hash(password)
        new_request = User_r(login_r = login, password_r = password,
                             face_r = face_id, company_r = company,
                             ip_r = ip, mac_r = mac,
                             location_r = location,
                             mail_r = email)
        session_r.add(new_request)
        session_r.commit()
    except Exception as e:
        session_r.rollback()
        print(f"Error: {e}")
    finally:
        session_r.close()


def get_10_requests_users():
    session_r = Session_r()
    try:
        data = session_r.query(User_r).limit(10).all()
        return data
    except Exception as e:
        session_r.rollback()
        print(f"Error: {e}")
    finally:
        session_r.close()

def get_10_requests_companies():
    session_r = Session_r()
    try:
        data = session_r.query(Company_r).limit(10).all()
        return data
    except Exception as e:
        session_r.rollback()
        print(f"Error: {e}")
    finally:
        session_r.close()

def remove_user_request_from_db(user_login):
    session_r = Session_r()
    try:
        request_user = session_r.query(User_r).filter(User_r.login_r == user_login).first()
        if request_user:
            session_r.delete(request_user)
            session_r.commit()
            print(f"Пользователь {user_login} успешно удален из базы заявок.")
        else:
            print(f"Пользователь {user_login} не найден в базе данных запросов.")
    except Exception as e:
        session_r.rollback()
        print(f"Ошибка при удалении пользователя из базы данных запросов: {e}")
    finally:
        session_r.close()

def remove_company_request_from_db(company_name):
    session_r = Session_r()
    try:
        request_company = session_r.query(Company_r).filter(Company_r.name_company_r == company_name).first()
        if request_company:
            session_r.delete(request_company)
            session_r.commit()
            print(f"Компания {company_name} успешно удалена из базы заявок.")
        else:
            print(f"Компания {company_name} не найдена в базе данных запросов.")
    except Exception as e:
        session_r.rollback()
        print(f"Ошибка при удалении компании из базы данных запросов: {e}")
    finally:
        session_r.close()


def company_reg(company_name_r, company_password_r, user_login_r, user_password_r, number_of_employee_r):
    session = Session()
    session_r = Session_r()
    company_name_r = get_sha256_hash(company_name_r)
    company_password_r = get_sha256_hash(company_password_r)
    user_login_r = get_sha256_hash(user_login_r)
    user_password_r = get_sha256_hash(user_password_r)

    info_comp = session.query(Company).filter_by(name_company=company_name_r).first()
    info_comp_r = session_r.query(Company_r).filter_by(name_company_r=company_name_r).first()

    if not info_comp and not info_comp_r:
        try:
            user_info = session.query(User).filter(User.login == user_login_r).first()
            if user_info and user_info.password == user_password_r:
                new_company_request = Company_r(name_company_r=company_name_r,
                                                password_company_r = company_password_r,
                                                owner_login_r=user_login_r,
                                                owner_ip_r = user_info.ip,
                                                owner_mac_r= user_info.mac,
                                                owner_location_r= user_info.location,
                                                number_of_employee_r=number_of_employee_r)
                session_r.add(new_company_request)
                session_r.commit()
                return True
            elif not user_info:
                return "user_not_found"
            else:
                return "wrong_password"
        except Exception as e:
            session_r.rollback()
            print(f"Error: {e}")
            return False
        finally:
            session_r.close()
            session.close()
    else:
        session.close()
        session_r.close()
        return "company_exists"





