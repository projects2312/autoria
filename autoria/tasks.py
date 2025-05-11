import os
import subprocess
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from celery_app import app

load_dotenv()

@app.task
def dump_and_scrape():
    print(">>> Starting the scraper...")

    try:
        subprocess.run("scrapy crawl auto", check=True, shell=True)
        print(">>> Scraper completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"!!! Error while running the scraper: {e}")
        return

    print(">>> Starting the database dump...")

    dump_dir = Path("dumps")
    dump_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dump_file = dump_dir / f"db_dump_{timestamp}.sql"

    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME")

    if not all([db_user, db_password, db_name]):
        print("!!! Missing required environment variables (DB_USER, DB_PASSWORD, DB_NAME).")
        return

    os.environ["PGPASSWORD"] = db_password

    dump_command = (
        f"pg_dump -U {db_user} -h {db_host} -p {db_port} "
        f"-F c -b -v -f {dump_file} {db_name}"
    )

    try:
        subprocess.run(dump_command, shell=True, check=True)
        print(f">>> Database dump successfully created: {dump_file}")
    except subprocess.CalledProcessError as e:
        print(f"!!! Error while creating the database dump: {e}")
