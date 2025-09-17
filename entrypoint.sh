#!/usr/bin/env bash
set -e

# Ожидание БД
until nc -z -v -w30 "$POSTGRES_HOST" "$POSTGRES_PORT"; do
echo "Ждем запуска PostgreSQL $POSTGRES_HOST:$POSTGRES_PORT..."
sleep 1
done

echo "PostgreSQL запущена!"

# Миграции и запуск
python manage.py migrate --noinput
python manage.py runserver 0.0.0.0:8000