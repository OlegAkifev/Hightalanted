from django.urls import path
from .views import (
    QuestionListCreateView,
    QuestionRetrieveDeleteView,
    AnswerCreateForQuestionView,
    AnswerRetrieveDeleteView,
)


urlpatterns = [
    # Вопросы
    path('questions/', QuestionListCreateView.as_view(), name='question-list-create'),
    path('questions/<int:pk>/', QuestionRetrieveDeleteView.as_view(), name='question-detail-delete'),
    # Ответы
    path('questions/<int:question_id>/answers/', AnswerCreateForQuestionView.as_view(), name='answer-create-for-question'),
    path('answers/<int:pk>/', AnswerRetrieveDeleteView.as_view(), name='answer-detail-delete'),
]