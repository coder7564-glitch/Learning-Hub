"""
URL patterns for quizzes.
"""
from django.urls import path
from .views import (
    QuizListView, QuizDetailView,
    QuestionListCreateView, QuestionDetailView,
    StartQuizView, SubmitQuizView,
    MyQuizAttemptsView, QuizAttemptDetailView,
    AllQuizAttemptsView, QuizStatisticsView
)

app_name = 'quizzes'

urlpatterns = [
    # Quizzes
    path('', QuizListView.as_view(), name='quiz_list'),
    path('<int:pk>/', QuizDetailView.as_view(), name='quiz_detail'),
    
    # Questions
    path('<int:quiz_id>/questions/', QuestionListCreateView.as_view(), name='question_list'),
    path('questions/<int:pk>/', QuestionDetailView.as_view(), name='question_detail'),
    
    # Quiz Taking
    path('start/', StartQuizView.as_view(), name='start_quiz'),
    path('submit/', SubmitQuizView.as_view(), name='submit_quiz'),
    
    # Attempts
    path('attempts/', MyQuizAttemptsView.as_view(), name='my_attempts'),
    path('attempts/<int:pk>/', QuizAttemptDetailView.as_view(), name='attempt_detail'),
    
    # Admin
    path('all-attempts/', AllQuizAttemptsView.as_view(), name='all_attempts'),
    path('<int:quiz_id>/statistics/', QuizStatisticsView.as_view(), name='quiz_statistics'),
]
