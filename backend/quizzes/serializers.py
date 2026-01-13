"""
Serializers for quizzes.
"""
from rest_framework import serializers
from .models import Quiz, Question, Answer, QuizAttempt, QuizResponse


class AnswerSerializer(serializers.ModelSerializer):
    """Serializer for answers (hides is_correct for students)."""
    
    class Meta:
        model = Answer
        fields = ['id', 'answer_text', 'order']


class AnswerAdminSerializer(serializers.ModelSerializer):
    """Serializer for answers (admin view with is_correct)."""
    
    class Meta:
        model = Answer
        fields = ['id', 'answer_text', 'is_correct', 'order']


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for questions (student view)."""
    
    answers = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = [
            'id', 'question_text', 'question_type',
            'points', 'order', 'answers'
        ]


class QuestionAdminSerializer(serializers.ModelSerializer):
    """Serializer for questions (admin view with correct answers)."""
    
    answers = AnswerAdminSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = [
            'id', 'question_text', 'question_type', 'explanation',
            'points', 'order', 'answers', 'created_at'
        ]


class QuestionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating questions with answers."""
    
    answers = AnswerAdminSerializer(many=True)
    
    class Meta:
        model = Question
        fields = [
            'quiz', 'question_text', 'question_type',
            'explanation', 'points', 'order', 'answers'
        ]
    
    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        question = Question.objects.create(**validated_data)
        
        for answer_data in answers_data:
            Answer.objects.create(question=question, **answer_data)
        
        return question
    
    def update(self, instance, validated_data):
        answers_data = validated_data.pop('answers', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if answers_data is not None:
            instance.answers.all().delete()
            for answer_data in answers_data:
                Answer.objects.create(question=instance, **answer_data)
        
        return instance


class QuizListSerializer(serializers.ModelSerializer):
    """Serializer for listing quizzes."""
    
    total_questions = serializers.ReadOnlyField()
    total_points = serializers.ReadOnlyField()
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'passing_score',
            'time_limit_minutes', 'max_attempts', 'is_required',
            'total_questions', 'total_points', 'order', 'created_at'
        ]


class QuizDetailSerializer(serializers.ModelSerializer):
    """Serializer for quiz details with questions."""
    
    questions = QuestionSerializer(many=True, read_only=True)
    total_questions = serializers.ReadOnlyField()
    total_points = serializers.ReadOnlyField()
    user_attempts = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'course', 'module', 'video',
            'passing_score', 'time_limit_minutes', 'max_attempts',
            'shuffle_questions', 'show_correct_answers', 'is_required',
            'questions', 'total_questions', 'total_points',
            'user_attempts', 'created_at'
        ]
    
    def get_user_attempts(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.attempts.filter(user=request.user).count()
        return 0


class QuizAdminSerializer(serializers.ModelSerializer):
    """Serializer for quiz admin view."""
    
    questions = QuestionAdminSerializer(many=True, read_only=True)
    total_questions = serializers.ReadOnlyField()
    total_points = serializers.ReadOnlyField()
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'course', 'module', 'video',
            'passing_score', 'time_limit_minutes', 'max_attempts',
            'shuffle_questions', 'show_correct_answers', 'is_required',
            'is_published', 'questions', 'total_questions', 'total_points',
            'order', 'created_at', 'updated_at'
        ]


class QuizCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating quizzes."""
    
    class Meta:
        model = Quiz
        fields = [
            'title', 'description', 'course', 'module', 'video',
            'passing_score', 'time_limit_minutes', 'max_attempts',
            'shuffle_questions', 'show_correct_answers', 'is_required',
            'is_published', 'order'
        ]


class QuizResponseSerializer(serializers.ModelSerializer):
    """Serializer for quiz responses."""
    
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    
    class Meta:
        model = QuizResponse
        fields = [
            'id', 'question', 'question_text', 'selected_answers',
            'text_response', 'is_correct', 'points_earned', 'answered_at'
        ]
        read_only_fields = ['is_correct', 'points_earned']


class QuizAttemptSerializer(serializers.ModelSerializer):
    """Serializer for quiz attempts."""
    
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    responses = QuizResponseSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'quiz', 'quiz_title', 'status', 'score', 'passed',
            'time_taken_seconds', 'started_at', 'completed_at', 'responses'
        ]
        read_only_fields = ['score', 'passed', 'started_at']


class StartQuizSerializer(serializers.Serializer):
    """Serializer for starting a quiz."""
    
    quiz_id = serializers.IntegerField()
    
    def validate_quiz_id(self, value):
        try:
            Quiz.objects.get(id=value, is_published=True)
        except Quiz.DoesNotExist:
            raise serializers.ValidationError("Quiz not found or not published.")
        return value


class SubmitAnswerSerializer(serializers.Serializer):
    """Serializer for submitting an answer."""
    
    question_id = serializers.IntegerField()
    selected_answer_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=[]
    )
    text_response = serializers.CharField(required=False, default='')


class SubmitQuizSerializer(serializers.Serializer):
    """Serializer for submitting a complete quiz."""
    
    attempt_id = serializers.IntegerField()
    responses = SubmitAnswerSerializer(many=True)
