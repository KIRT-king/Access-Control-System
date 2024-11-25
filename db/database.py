import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()

Session = sessionmaker(bind=engine)

def create_tables():
    try:
        Base.metadata.create_all(engine)
        print("Таблица 'users' успешно создана!")
    except Exception as e:
        print(f"Ошибка при создании таблицы: {e}")
