"""
Views for quizzes.
"""
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Avg

from .models import Quiz, Question, Answer, QuizAttempt, QuizResponse
from .serializers import (
    QuizListSerializer, QuizDetailSerializer, QuizAdminSerializer,
    QuizCreateSerializer, QuestionCreateSerializer, QuestionAdminSerializer,
    QuizAttemptSerializer, StartQuizSerializer, SubmitQuizSerializer
)
from accounts.permissions import IsAdmin, IsAdminOrReadOnly


class QuizListView(generics.ListCreateAPIView):
    """List and create quizzes."""
    
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['course', 'module', 'video', 'is_required']
    search_fields = ['title', 'description']
    
    def get_queryset(self):
        queryset = Quiz.objects.all()
        user = self.request.user
        
        if not user.is_authenticated or not user.is_admin:
            queryset = queryset.filter(is_published=True)
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return QuizCreateSerializer
        if self.request.user.is_authenticated and self.request.user.is_admin:
            return QuizAdminSerializer
        return QuizListSerializer


class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete quiz."""
    
    permission_classes = [IsAdminOrReadOnly]
    
    def get_queryset(self):
        queryset = Quiz.objects.prefetch_related('questions__answers')
        user = self.request.user
        
        if not user.is_authenticated or not user.is_admin:
            queryset = queryset.filter(is_published=True)
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return QuizCreateSerializer
        if self.request.user.is_authenticated and self.request.user.is_admin:
            return QuizAdminSerializer
        return QuizDetailSerializer


class QuestionListCreateView(generics.ListCreateAPIView):
    """List and create questions for a quiz."""
    
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    
    def get_queryset(self):
        quiz_id = self.kwargs.get('quiz_id')
        return Question.objects.filter(quiz_id=quiz_id).prefetch_related('answers')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return QuestionCreateSerializer
        return QuestionAdminSerializer


class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete question."""
    
    queryset = Question.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return QuestionCreateSerializer
        return QuestionAdminSerializer


class StartQuizView(APIView):
    """Start a quiz attempt."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = StartQuizSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        quiz = Quiz.objects.get(id=serializer.validated_data['quiz_id'])
        user = request.user
        
        # Check max attempts
        if quiz.max_attempts > 0:
            attempts_count = QuizAttempt.objects.filter(
                user=user,
                quiz=quiz,
                status=QuizAttempt.Status.COMPLETED
            ).count()
            
            if attempts_count >= quiz.max_attempts:
                return Response(
                    {'error': f'Maximum attempts ({quiz.max_attempts}) reached.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Check for existing in-progress attempt
        existing_attempt = QuizAttempt.objects.filter(
            user=user,
            quiz=quiz,
            status=QuizAttempt.Status.IN_PROGRESS
        ).first()
        
        if existing_attempt:
            return Response(QuizAttemptSerializer(existing_attempt).data)
        
        # Create new attempt
        attempt = QuizAttempt.objects.create(
            user=user,
            quiz=quiz,
            status=QuizAttempt.Status.IN_PROGRESS
        )
        
        return Response(
            QuizAttemptSerializer(attempt).data,
            status=status.HTTP_201_CREATED
        )


class SubmitQuizView(APIView):
    """Submit quiz answers and complete attempt."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = SubmitQuizSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            attempt = QuizAttempt.objects.get(
                id=serializer.validated_data['attempt_id'],
                user=request.user,
                status=QuizAttempt.Status.IN_PROGRESS
            )
        except QuizAttempt.DoesNotExist:
            return Response(
                {'error': 'Quiz attempt not found or already completed.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check time limit
        if attempt.quiz.time_limit_minutes > 0:
            elapsed_seconds = (timezone.now() - attempt.started_at).total_seconds()
            if elapsed_seconds > attempt.quiz.time_limit_minutes * 60:
                attempt.status = QuizAttempt.Status.TIMED_OUT
                attempt.completed_at = timezone.now()
                attempt.time_taken_seconds = int(elapsed_seconds)
                attempt.save()
                return Response(
                    {'error': 'Quiz time limit exceeded.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Process responses
        for response_data in serializer.validated_data['responses']:
            try:
                question = Question.objects.get(
                    id=response_data['question_id'],
                    quiz=attempt.quiz
                )
            except Question.DoesNotExist:
                continue
            
            quiz_response, created = QuizResponse.objects.get_or_create(
                attempt=attempt,
                question=question
            )
            
            # Set selected answers
            if response_data.get('selected_answer_ids'):
                quiz_response.selected_answers.set(
                    Answer.objects.filter(
                        id__in=response_data['selected_answer_ids'],
                        question=question
                    )
                )
            
            # Set text response
            if response_data.get('text_response'):
                quiz_response.text_response = response_data['text_response']
            
            quiz_response.check_answer()
            quiz_response.save()
        
        # Complete attempt
        attempt.status = QuizAttempt.Status.COMPLETED
        attempt.completed_at = timezone.now()
        attempt.time_taken_seconds = int((attempt.completed_at - attempt.started_at).total_seconds())
        attempt.calculate_score()
        attempt.save()
        
        return Response(QuizAttemptSerializer(attempt).data)


class MyQuizAttemptsView(generics.ListAPIView):
    """List current user's quiz attempts."""
    
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['quiz', 'status', 'passed']
    
    def get_queryset(self):
        return QuizAttempt.objects.filter(
            user=self.request.user
        ).select_related('quiz').prefetch_related('responses')


class QuizAttemptDetailView(generics.RetrieveAPIView):
    """View quiz attempt details."""
    
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return QuizAttempt.objects.all()
        return QuizAttempt.objects.filter(user=user)


# Admin Views
class AllQuizAttemptsView(generics.ListAPIView):
    """List all quiz attempts (admin only)."""
    
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    filterset_fields = ['quiz', 'user', 'status', 'passed']
    search_fields = ['user__email', 'quiz__title']
    
    def get_queryset(self):
        return QuizAttempt.objects.select_related('user', 'quiz').all()


class QuizStatisticsView(APIView):
    """Get quiz statistics (admin only)."""
    
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    
    def get(self, request, quiz_id):
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            return Response(
                {'error': 'Quiz not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        attempts = QuizAttempt.objects.filter(
            quiz=quiz,
            status=QuizAttempt.Status.COMPLETED
        )
        
        stats = {
            'quiz_id': quiz.id,
            'quiz_title': quiz.title,
            'total_attempts': attempts.count(),
            'average_score': attempts.aggregate(avg=Avg('score'))['avg'] or 0,
            'pass_rate': (
                attempts.filter(passed=True).count() / attempts.count() * 100
                if attempts.count() > 0 else 0
            ),
            'average_time_seconds': attempts.aggregate(avg=Avg('time_taken_seconds'))['avg'] or 0,
        }
        
        return Response(stats)
