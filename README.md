# API-сервис «Вопросы и ответы» (Django + DRF + PostgreSQL + Docker)


REST API для вопросов и ответов. Реализованы все методы по ТЗ, валидация, каскадное удаление ответов, логгирование и тесты на pytest.


## 🚀 Быстрый старт(Необходим установленный Docker)

1) Заходим в папку, в которую будем клонировать репозиторий
2) Делаем git clone git@github.com:OlegAkifev/Hightalanted.git
3) cd Hightalanted/
4) Подготовка окружения
    cp .env.example .env (при необходимости, поправьте значения в .env)
5) Запуск
    sudo docker compose up --build
    Сервис будет доступен на: http://localhost:8000
6) Прогоним тесты
    sudo docker compose exec web pytest -vv

7) Доступные АПИ методы можно посмотреть на странице 
    http://localhost:8000/api/schema/swagger-ui/

🔌 Эндпоинты

    Вопросы (Questions)

        GET /questions/ — список всех вопросов (новые сверху)

        POST /questions/ — создать новый вопрос

        GET /questions/{id} — получить вопрос и все ответы на него

        DELETE /questions/{id} — удалить вопрос (ответы удаляются каскадно)

    Ответы (Answers)

        POST /questions/{id}/answers/ — добавить ответ к вопросу

        GET /answers/{id} — получить конкретный ответ

        DELETE /answers/{id} — удалить ответ


🧠 Бизнес-логика

    Нельзя создать ответ к несуществующему вопросу (вернётся 404).

    Один и тот же пользователь может оставлять несколько ответов на один вопрос.

    При удалении вопроса все его ответы удаляются каскадно (on_delete=CASCADE).

    Пустые тексты вопроса/ответа и пустой user_id запрещены валидаторами DRF.

🧪 Примеры (cURL)

    Создать вопрос
        curl -X POST http://localhost:8000/questions/ -H 'Content-Type: application/json' -d '{"text": "Что такое REST?"}'

    Получить список вопросов
        curl http://localhost:8000/questions/
    
    Получить вопрос с ответами
        curl http://localhost:8000/questions/1/
    
    Добавить ответ к вопросу
        curl -X POST http://localhost:8000/questions/1/answers/ -H 'Content-Type: application/json' -d '{"user_id": "user-123", "text": "Архитектурный стиль для веб-сервисов."}'
    
    Получить ответ
        curl http://localhost:8000/answers/1/

    Удалить ответ
        curl -X DELETE http://localhost:8000/answers/1/

    Удалить вопрос (и все его ответы)
        curl -X DELETE http://localhost:8000/questions/1/


🧱 Архитектура

    Django + DRF: модели (question_answer/models.py), сериализаторы (question_answer/serializers.py), представления (question_answer/views.py), маршрутизация (question_answer/urls.py).

    Валидация: DRF-сериализаторы запрещают пустые поля (strip() и проверки).

    Каскадное удаление: Answer.question = ForeignKey(..., on_delete=CASCADE).

    Логгирование: базовая настройка в settings.py (logger = question_answer).

    Тесты: pytest + pytest-django, проверяют основной сценарий и валидацию.

    Docker: Dockerfile + docker-compose.yml с Postgres 16.

    Документация: Swagger UI 

🔧 Конфигурация

    Настройки берутся из .env (POSTGRES_*, DJANGO_*).

📜 Лицензия MIT

    ---

    > Готово! Код и инструкции выше — это полноценный репозиторий. Скопируйте в папку, создайте `.env` из `.env.example` и запускайте `docker compose up --build`.
