from __future__ import annotations
from rest_framework import serializers
from .models import Question, Answer


class QuestionSerializer(serializers.ModelSerializer):
    text = serializers.CharField()

    class Meta:
        model = Question
        fields = ['id', 'text', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_text(self, value: str) -> str:
        if not value or not value.strip():
            raise serializers.ValidationError('Текст вопроса не может быть пустым.')
        return value.strip()


class AnswerSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField()
    text = serializers.CharField()

    class Meta:
        model = Answer
        fields = ['id', 'question_id', 'user_id', 'text', 'created_at']
        read_only_fields = ['id', 'created_at', 'question_id']

    def validate_user_id(self, value: str) -> str:
        if not value or not value.strip():
            raise serializers.ValidationError('user_id обязателен.')
        return value.strip()

    def validate_text(self, value: str) -> str:
        if not value or not value.strip():
            raise serializers.ValidationError('Текст ответа не может быть пустым.')
        return value.strip()


class QuestionDetailSerializer(QuestionSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta(QuestionSerializer.Meta):
        fields = QuestionSerializer.Meta.fields + ['answers']