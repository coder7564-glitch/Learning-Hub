"""
Admin configuration for quizzes.
"""
from django.contrib import admin
from .models import Quiz, Question, Answer, QuizAttempt, QuizResponse


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    show_change_link = True


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'module', 'passing_score', 'is_required', 'is_published')
    list_filter = ('is_published', 'is_required', 'course')
    search_fields = ('title', 'description')
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'question_type', 'points', 'order')
    list_filter = ('question_type', 'quiz')
    search_fields = ('question_text',)
    inlines = [AnswerInline]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'status', 'score', 'passed', 'started_at', 'completed_at')
    list_filter = ('status', 'passed', 'quiz')
    search_fields = ('user__email', 'quiz__title')
    raw_id_fields = ('user', 'quiz')


@admin.register(QuizResponse)
class QuizResponseAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'is_correct', 'points_earned')
    list_filter = ('is_correct',)
    raw_id_fields = ('attempt', 'question')
