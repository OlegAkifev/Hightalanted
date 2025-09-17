from __future__ import annotations
import logging
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response


from .models import Question, Answer
from .serializers import (
    QuestionSerializer,
    QuestionDetailSerializer,
    AnswerSerializer,
)


logger = logging.getLogger('question_answer')


# GET /questions/ | POST /questions/
class QuestionListCreateView(generics.ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def create(self, request: Request, *args, **kwargs) -> Response:
        logger.info('Создание вопроса: %s', request.data)
        return super().create(request, *args, **kwargs)


# GET /questions/{id} | DELETE /questions/{id}
class QuestionRetrieveDeleteView(generics.RetrieveDestroyAPIView):
    queryset = Question.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return QuestionDetailSerializer
        return QuestionSerializer

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        q: Question = self.get_object()
        logger.info('Удаление вопроса id=%s (каскадно удалятся ответы)', q.id)
        return super().destroy(request, *args, **kwargs)


# POST /questions/{id}/answers/
class AnswerCreateForQuestionView(generics.CreateAPIView):
    serializer_class = AnswerSerializer

    def create(self, request: Request, *args, **kwargs) -> Response:
        question_id = kwargs.get('question_id')
        question = get_object_or_404(Question, pk=question_id)
        logger.info('Создание ответа для вопроса id=%s: %s', question_id, request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(question=question)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# GET /answers/{id} | DELETE /answers/{id}
class AnswerRetrieveDeleteView(generics.RetrieveDestroyAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        a: Answer = self.get_object()
        logger.info('Удаление ответа id=%s для вопроса id=%s', a.id, a.question_id)
        return super().destroy(request, *args, **kwargs)