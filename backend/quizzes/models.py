"""
Models for quizzes and assessments.
"""
from django.db import models
from django.conf import settings
from courses.models import Course, Module, Video


class Quiz(models.Model):
    """Quiz/Assessment model."""
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Can be attached to course, module, or video
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='quizzes',
        null=True,
        blank=True
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='quizzes',
        null=True,
        blank=True
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name='quizzes',
        null=True,
        blank=True
    )
    
    passing_score = models.PositiveIntegerField(default=70, help_text="Minimum score to pass (%)")
    time_limit_minutes = models.PositiveIntegerField(default=0, help_text="0 for no limit")
    max_attempts = models.PositiveIntegerField(default=0, help_text="0 for unlimited")
    shuffle_questions = models.BooleanField(default=False)
    show_correct_answers = models.BooleanField(default=True)
    
    is_required = models.BooleanField(default=False, help_text="Required for course completion")
    is_published = models.BooleanField(default=True)
    
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'quiz'
        verbose_name_plural = 'quizzes'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def total_questions(self):
        return self.questions.count()
    
    @property
    def total_points(self):
        return self.questions.aggregate(total=models.Sum('points'))['total'] or 0


class Question(models.Model):
    """Question model for quizzes."""
    
    class QuestionType(models.TextChoices):
        MULTIPLE_CHOICE = 'multiple_choice', 'Multiple Choice'
        TRUE_FALSE = 'true_false', 'True/False'
        MULTIPLE_SELECT = 'multiple_select', 'Multiple Select'
        SHORT_ANSWER = 'short_answer', 'Short Answer'
    
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    
    question_text = models.TextField()
    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
        default=QuestionType.MULTIPLE_CHOICE
    )
    
    explanation = models.TextField(blank=True, help_text="Explanation shown after answering")
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'question'
        verbose_name_plural = 'questions'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}"


class Answer(models.Model):
    """Answer option for questions."""
    
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'answer'
        verbose_name_plural = 'answers'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.question} - {self.answer_text[:50]}"


class QuizAttempt(models.Model):
    """Record of a student's quiz attempt."""
    
    class Status(models.TextChoices):
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        TIMED_OUT = 'timed_out', 'Timed Out'
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_attempts'
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS
    )
    
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    passed = models.BooleanField(default=False)
    time_taken_seconds = models.PositiveIntegerField(default=0)
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'quiz attempt'
        verbose_name_plural = 'quiz attempts'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.quiz.title} - {self.score}%"
    
    def calculate_score(self):
        """Calculate the score based on responses."""
        total_points = self.quiz.total_points
        if total_points == 0:
            return 0
        
        earned_points = sum(
            response.question.points
            for response in self.responses.filter(is_correct=True)
        )
        
        self.score = (earned_points / total_points) * 100
        self.passed = self.score >= self.quiz.passing_score
        return self.score


class QuizResponse(models.Model):
    """Student's response to a quiz question."""
    
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    
    # For multiple choice / true-false / multiple select
    selected_answers = models.ManyToManyField(Answer, blank=True)
    
    # For short answer
    text_response = models.TextField(blank=True)
    
    is_correct = models.BooleanField(default=False)
    points_earned = models.PositiveIntegerField(default=0)
    
    answered_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'quiz response'
        verbose_name_plural = 'quiz responses'
        unique_together = ['attempt', 'question']
    
    def __str__(self):
        return f"{self.attempt} - {self.question}"
    
    def check_answer(self):
        """Check if the response is correct."""
        question = self.question
        
        if question.question_type in [Question.QuestionType.MULTIPLE_CHOICE, Question.QuestionType.TRUE_FALSE]:
            correct_answer = question.answers.filter(is_correct=True).first()
            selected = self.selected_answers.first()
            self.is_correct = selected == correct_answer if correct_answer and selected else False
        
        elif question.question_type == Question.QuestionType.MULTIPLE_SELECT:
            correct_answers = set(question.answers.filter(is_correct=True).values_list('id', flat=True))
            selected_answers = set(self.selected_answers.values_list('id', flat=True))
            self.is_correct = correct_answers == selected_answers
        
        elif question.question_type == Question.QuestionType.SHORT_ANSWER:
            # Basic check - can be enhanced with fuzzy matching
            correct_answer = question.answers.filter(is_correct=True).first()
            if correct_answer:
                self.is_correct = self.text_response.strip().lower() == correct_answer.answer_text.strip().lower()
        
        self.points_earned = question.points if self.is_correct else 0
        return self.is_correct
