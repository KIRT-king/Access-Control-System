from db.database import create_tables
from db.commands import create_new_user

# Создаем таблицы (в database.py) перед выполнением любых операций с базой данных
create_tables()

from regestration.database_req import create_tables_r
from regestration.commands_req import create_request

create_tables_r()
# create_request("kirt3", "1234")
