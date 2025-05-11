#!/bin/bash

# Ожидать доступности базы данных
while ! nc -z $DB_HOST $DB_PORT; do
  echo "Waiting for database..."
  sleep 3
done

echo "Database is up!"

alembic upgrade head
celery -A celery_app worker -l info -P eventlet
