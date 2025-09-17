from __future__ import annotations
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

client = APIClient()


class TestQnAAPI:
    def test_create_question_and_answer_flow(self):
        # Создаём вопрос
        q_payload = {"text": "Что такое REST API?"}
        r = client.post(reverse('question-list-create'), data=q_payload, format='json')
        assert r.status_code == 201
        q = r.json()
        q_id = q['id']
        assert q['text'] == q_payload['text']

        # Добавляем два ответа к вопросу
        a1 = {"user_id": "user-123", "text": "Стиль архитектуры для веб-сервисов."}
        a2 = {"user_id": "user-456", "text": "Набор принципов взаимодействия по HTTP."}

        r1 = client.post(reverse('answer-create-for-question', kwargs={'question_id': q_id}), data=a1, format='json')
        r2 = client.post(reverse('answer-create-for-question', kwargs={'question_id': q_id}), data=a2, format='json')
        assert r1.status_code == 201 and r2.status_code == 201

        # Получаем вопрос с вложенными ответами
        r = client.get(reverse('question-detail-delete', kwargs={'pk': q_id}))
        assert r.status_code == 200
        data = r.json()
        assert data['id'] == q_id
        assert len(data['answers']) == 2

        # Удаляем вопрос — ответы должны удалиться каскадно
        r = client.delete(reverse('question-detail-delete', kwargs={'pk': q_id}))
        assert r.status_code == 204

        # Проверяем, что ответы недоступны
        ans_ids = [r1.json()['id'], r2.json()['id']]
        for ans_id in ans_ids:
            r = client.get(reverse('answer-detail-delete', kwargs={'pk': ans_id}))
            assert r.status_code == 404

    def test_validation(self):
        # Пустой текст вопроса запрещён
        r = client.post(reverse('question-list-create'), data={"text": " "}, format='json')
        assert r.status_code == 400

        # Пустой user_id и текст ответа запрещены
        r = client.post(reverse('question-list-create'), data={"text": "Вопрос"}, format='json')
        q_id = r.json()['id']

        bad_payload = {"user_id": " ", "text": " "}
        r = client.post(
            reverse('answer-create-for-question', kwargs={'question_id': q_id}),
            data=bad_payload,
            format='json'
        )
        assert r.status_code == 400


    def test_list_questions(self):
        # создаём два вопроса
        r1 = client.post(reverse('question-list-create'), data={"text": "Q1"}, format='json')
        q1_id = r1.json()['id']
        r2 = client.post(reverse('question-list-create'), data={"text": "Q2"}, format='json')
        q2_id = r2.json()['id']

        # GET /questions/ — список 
        r = client.get(reverse('question-list-create'))
        assert r.status_code == 200
        items = r.json()
        assert isinstance(items, list) and len(items) >= 2
        # ожидаем порядок по -created_at (последний созданный — первым)
        returned_ids = [item['id'] for item in items[:2]]
        assert returned_ids == [q2_id, q1_id]

    def test_get_answer_by_id(self):
        # создаём вопрос и ответ
        r = client.post(reverse('question-list-create'), data={"text": "Вопрос"}, format='json')
        q_id = r.json()['id']
        a_payload = {"user_id": "user-xyz", "text": "Ответ текст"}
        r = client.post(
            reverse('answer-create-for-question', kwargs={'question_id': q_id}),
            data=a_payload, format='json'
        )
        assert r.status_code == 201
        a_id = r.json()['id']

        # GET /answers/{id}
        r = client.get(reverse('answer-detail-delete', kwargs={'pk': a_id}))
        assert r.status_code == 200
        data = r.json()
        assert data['id'] == a_id
        assert data['user_id'] == "user-xyz"
        assert data['text'] == "Ответ текст"
        assert data['question_id'] == q_id

    def test_delete_answer_by_id(self):
        # создаём вопрос и ответ
        r = client.post(reverse('question-list-create'), data={"text": "Вопрос"}, format='json')
        q_id = r.json()['id']
        r = client.post(
            reverse('answer-create-for-question', kwargs={'question_id': q_id}),
            data={"user_id": "u1", "text": "del me"}, format='json'
        )
        a_id = r.json()['id']

        # DELETE /answers/{id}
        r = client.delete(reverse('answer-detail-delete', kwargs={'pk': a_id}))
        assert r.status_code == 204

        # проверяем, что удалён
        r = client.get(reverse('answer-detail-delete', kwargs={'pk': a_id}))
        assert r.status_code == 404

    def test_create_answer_for_nonexistent_question_404(self):
        # POST /questions/{id}/answers/ на несуществующий вопрос
        r = client.post(
            reverse('answer-create-for-question', kwargs={'question_id': 999999}),
            data={"user_id": "u1", "text": "hi"},
            format='json'
        )
        assert r.status_code == 404

    def test_same_user_can_post_multiple_answers_for_one_question(self):
        # Один и тот же пользователь может оставить несколько ответов к одному вопросу
        r = client.post(reverse('question-list-create'), data={"text": "Вопрос"}, format='json')
        q_id = r.json()['id']

        payload = {"user_id": "same-user", "text": "Ответ #1"}
        r1 = client.post(reverse('answer-create-for-question', kwargs={'question_id': q_id}), data=payload, format='json')
        assert r1.status_code == 201

        payload2 = {"user_id": "same-user", "text": "Ответ #2"}
        r2 = client.post(reverse('answer-create-for-question', kwargs={'question_id': q_id}), data=payload2, format='json')
        assert r2.status_code == 201

        # убеждаемся, что оба ответа есть в детальном представлении вопроса
        r = client.get(reverse('question-detail-delete', kwargs={'pk': q_id}))
        assert r.status_code == 200
        data = r.json()
        texts = [a['text'] for a in data.get('answers', [])]
        assert "Ответ #1" in texts and "Ответ #2" in texts

    def test_delete_nonexistent_question_returns_404(self):
        r = client.delete(reverse('question-detail-delete', kwargs={'pk': 987654}))
        assert r.status_code == 404

    def test_delete_nonexistent_answer_returns_404(self):
        r = client.delete(reverse('answer-detail-delete', kwargs={'pk': 987654}))
        assert r.status_code == 404

    def test_list_questions_empty(self):
        # GET /questions/ — когда в БД нет вопросов
        r = client.get(reverse('question-list-create'))
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert data == []

    def test_schema_fields(self):
        # Создаём вопрос
        r = client.post(reverse('question-list-create'), data={"text": "Схема?"}, format='json')
        assert r.status_code == 201
        q = r.json()

        # Проверяем ключи и типы
        for key in ("id", "text", "created_at"):
            assert key in q
        assert isinstance(q["id"], int)
        assert isinstance(q["text"], str)
        assert isinstance(q["created_at"], str)

        q_id = q["id"]

        # Создаём ответ к вопросу
        r = client.post(
            reverse('answer-create-for-question', kwargs={"question_id": q_id}),
            data={"user_id": "u1", "text": "ok"},
            format='json'
        )
        assert r.status_code == 201
        a = r.json()

        # Проверяем схему ответа
        for key in ("id", "question_id", "user_id", "text", "created_at"):
            assert key in a
        assert isinstance(a["id"], int)
        assert a["question_id"] == q_id
        assert isinstance(a["user_id"], str)
        assert isinstance(a["text"], str)
        assert isinstance(a["created_at"], str)

        # В детальном представлении вопроса должен быть список answers с нужной схемой
        r = client.get(reverse('question-detail-delete', kwargs={'pk': q_id}))
        assert r.status_code == 200
        data = r.json()
        assert "answers" in data and isinstance(data["answers"], list)
        assert any(ans["id"] == a["id"] for ans in data["answers"])
        for ans in data["answers"]:
            for key in ("id", "question_id", "user_id", "text", "created_at"):
                assert key in ans