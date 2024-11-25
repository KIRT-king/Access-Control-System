from sqlalchemy import Column, String, Integer, LargeBinary
from regestration.database_req import Base_r

class User_r(Base_r):
    __tablename__ = 'users_r'
    id_r = Column(Integer, primary_key=True)
    login_r = Column(String(255), nullable=False, unique=True)
    password_r = Column(String(255), nullable=False)
    face_r = Column(LargeBinary, nullable=True)
    company_r = Column(String(255), nullable=False)
    ip_r = Column(LargeBinary, nullable=False)
    mac_r = Column(LargeBinary, nullable=False)
    location_r = Column(LargeBinary, nullable=False)
    mail_r = Column(LargeBinary, nullable=False)

class Company_r(Base_r):
    __tablename__ = "company_r"
    id_r = Column(Integer, primary_key=True)
    name_company_r = Column(String(255), nullable=False, unique=True)
    password_company_r = Column(String(255), nullable=False)
    owner_login_r = Column(String(255), nullable=False)
    owner_ip_r = Column(LargeBinary, nullable=False)
    owner_mac_r = Column(LargeBinary, nullable=False)
    owner_location_r = Column(LargeBinary, nullable=False)
    number_of_employee_r = Column(Integer, nullable=False)
