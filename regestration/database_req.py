import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
DATABASE_URL_r = os.getenv("REGDATABSE_URL")

engine_r = create_engine(DATABASE_URL_r, echo=True)
Base_r = declarative_base()
Session_r = sessionmaker(bind=engine_r)

def create_tables_r():
    try:
        Base_r.metadata.create_all(engine_r)
        print("Таблица 'users_r' успешно создана!")
    except Exception as e:
        print(f"Ошибка при создании таблицы (users_r): {e}")
