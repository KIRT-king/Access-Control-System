from sqlalchemy import Column, Integer, String, LargeBinary
from db.database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    login = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    face = Column(LargeBinary, nullable=True)
    company = Column(String(255), nullable=False)
    level = Column(Integer, nullable=False)
    clas = Column(String(255), nullable=False)
    ip = Column(LargeBinary, nullable=False)
    mac = Column(LargeBinary, nullable=False)
    location = Column(LargeBinary, nullable=False)
    mail = Column(LargeBinary, nullable=False)
    user_status = Column(String(255), nullable=False)

class Company(Base):
    __tablename__ = "company"
    id = Column(Integer, primary_key=True)
    name_company = Column(String(255), nullable=False, unique=True)
    password_company = Column(String(255), nullable=False)
    owner_login = Column(String(255), nullable=False)
    owner_ip = Column(LargeBinary, nullable=False)
    owner_mac = Column(LargeBinary, nullable=False)
    owner_location = Column(LargeBinary, nullable=False)
    number_of_employee = Column(Integer, nullable=False)