import asyncio
from elasticsearch import AsyncElasticsearch
from datetime import datetime

# Настройка асинхронного подключения
es = AsyncElasticsearch(
    ["https://localhost:9200"],
    http_auth=("elastic", "-YlW0dKq75ZJV-9WSe=o"),
    verify_certs=False
)

# Проверка подключения
async def check_connection():
    if await es.ping():
        print("Подключение успешно!")
    else:
        print("Ошибка подключения.")
        await es.close()
        exit()

# Асинхронное логирование
async def log(index, message, level="INFO"):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": message,
    }
    await es.index(index=index, body=log_entry)

# Логирование действий
async def log_login(login):
    await log("system_logs", f"Пользователь {login} вошел в систему")

async def log_registration(login, mac_address=None):
    if mac_address:
        await log("system_logs", f"Пользователь {login} с mac {mac_address} зарегистрирован")
    else:
        await log("system_logs", f"Компания {login} зарегистрирована")

async def log_level_change(login, old_level, new_level):
    await log("system_logs", f"Пользователь {login} повысил уровень с {old_level} на {new_level}")

