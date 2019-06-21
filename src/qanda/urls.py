from django.urls import path
from .views import (
    AskQuestionView,
    QuestionDetailView,
    CreateAnswerView,
)
app_name = 'qanda'
urlpatterns = [
    path('ask',AskQuestionView.as_view(), name='ask'),
    path('q/<int:pk>',QuestionDetailView.as_view(),name="question_detail"),
    path('q/<int:pk>/answer',CreateAnswerView.as_view(),name="answer_question")
]