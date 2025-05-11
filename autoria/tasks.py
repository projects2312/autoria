import os
import subprocess
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from celery_app import app

load_dotenv()

@app.task
def dump_and_scrape():
    print(">>> Запуск скрапера...")

    # Запуск Scrapy-паука
    try:
        subprocess.run("scrapy crawl auto", check=True, shell=True)
        print(">>> Скрапер успешно завершил работу.")
    except subprocess.CalledProcessError as e:
        print(f"!!! Ошибка при запуске скрапера: {e}")
        return

    print(">>> Начинается создание дампа базы данных...")

    # Создание директории для дампов, если не существует
    dump_dir = Path("dumps")
    dump_dir.mkdir(exist_ok=True)

    # Формирование имени дампа с текущим временем
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dump_file = dump_dir / f"db_dump_{timestamp}.sql"

    # Получение переменных окружения
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME")

    # Проверка обязательных переменных
    if not all([db_user, db_password, db_name]):
        print("!!! Отсутствуют необходимые переменные окружения (DB_USER, DB_PASSWORD, DB_NAME).")
        return

    # Установка пароля для pg_dump
    os.environ["PGPASSWORD"] = db_password

    # Команда для создания дампа
    dump_command = (
        f"pg_dump -U {db_user} -h {db_host} -p {db_port} "
        f"-F c -b -v -f {dump_file} {db_name}"
    )

    # Выполнение команды дампа
    try:
        subprocess.run(dump_command, shell=True, check=True)
        print(f">>> Дамп базы данных успешно создан: {dump_file}")
    except subprocess.CalledProcessError as e:
        print(f"!!! Ошибка при создании дампа базы данных: {e}")
