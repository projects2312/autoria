# AutoRia Scraper

Проєкт для збору даних про вживані автомобілі з сайту [auto.ria.com](https://auto.ria.com) з використанням Scrapy, Selenium, Celery та PostgreSQL. Також реалізовано створення дампу бази даних після кожного запуску скрапінгу.

## 📦 Стек технологій

- Python 3
- Scrapy
- Selenium (через Chrome WebDriver)
- Celery + Redis (для планування задач)
- PostgreSQL
- Docker + Docker Compose
- .env (для конфігурації)

## 🚀 Функціональність

- Скрапінг оголошень з авто
- Отримання телефону продавця через Selenium
- Збереження даних у PostgreSQL
- Щоденний запуск задачі о 12:00 за допомогою Celery Beat
- Автоматичне створення дампу бази даних після скрапінгу

## ⚙️ Встановлення

1. Клонуйте репозиторій:

```bash
git clone https://github.com/projects2312/autoria.git
```

2. Скопіюйте .env.sample -> .env, заповніть даними

## ⚠️ Примітка щодо запуску

Для коректної роботи проекту може знадобитися два етапи запуску через Docker. Це пов'язано з тим, що на першому етапі, коли ви запускаєте контейнер, база даних може ще не бути повністю готова до використання, тому під час першого запуску деякі сервіси можуть не знайти базу даних або виникнуть інші залежності.

3. Виконайте:

```bash
docker-compose --build
```

## Структура

```
├── autoria/
│   ├── spiders/
│   │   └── auto.py
│   ├── tasks.py
│   └── __init__.py
├── db/
│   ├── models.py               # SQLAlchemy models
│   └── engine.py               # DB session setup
├── celery_app.py               # Celery config
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env                        # Environment variables
├── dumps/                     
└── README.md
```