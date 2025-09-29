from django.contrib import admin
from .models import Category, Course, Lesson, Enrollment, LessonProgress, Review, Quiz, Question, Answer, QuizAttempt, StudentAnswer


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active', 'order']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ['title', 'slug', 'lesson_type', 'order', 'duration_minutes', 'is_preview', 'is_published']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'instructor', 'difficulty', 'is_free', 'price', 'status', 'is_published', 'is_featured', 'created_at']
    list_filter = ['category', 'difficulty', 'is_free', 'status', 'is_published', 'is_featured', 'created_at']
    search_fields = ['title', 'description', 'instructor__username']
    list_editable = ['status', 'is_published', 'is_featured']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LessonInline]
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'slug', 'category', 'instructor', 'thumbnail')
        }),
        ('Contenu', {
            'fields': ('description', 'short_description', 'video_intro', 'prerequisites', 'learning_objectives')
        }),
        ('Métadonnées', {
            'fields': ('difficulty', 'duration_hours', 'language')
        }),
        ('Prix et accès', {
            'fields': ('is_free', 'price')
        }),
        ('Publication', {
            'fields': ('status', 'is_published', 'is_featured')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(instructor=request.user)
        return qs


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'lesson_type', 'order', 'duration_minutes', 'is_preview', 'is_published']
    list_filter = ['lesson_type', 'is_preview', 'is_published', 'course__category']
    search_fields = ['title', 'course__title']
    list_editable = ['order', 'is_preview', 'is_published']
    prepopulated_fields = {'slug': ('title',)}
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(course__instructor=request.user)
        return qs


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'enrolled_at', 'progress_percentage', 'is_completed', 'completed_at']
    list_filter = ['is_completed', 'enrolled_at', 'course__category']
    search_fields = ['user__username', 'user__email', 'course__title']
    readonly_fields = ['enrolled_at', 'completed_at']
    date_hierarchy = 'enrolled_at'


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'lesson', 'is_completed', 'completed_at', 'time_spent_minutes']
    list_filter = ['is_completed', 'lesson__lesson_type']
    search_fields = ['enrollment__user__username', 'lesson__title']
    readonly_fields = ['completed_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['course', 'user', 'rating', 'title', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['course__title', 'user__username', 'title', 'content']
    list_editable = ['is_approved']
    readonly_fields = ['created_at', 'updated_at']


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 2


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'passing_score', 'max_attempts', 'is_active']
    list_filter = ['is_active', 'lesson__course__category']
    search_fields = ['title', 'lesson__title']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'question_text_short', 'question_type', 'points', 'order', 'has_correct_answers']
    list_filter = ['question_type', 'quiz__lesson__course__category', 'quiz']
    search_fields = ['question_text', 'quiz__title']
    inlines = [AnswerInline]
    ordering = ['quiz', 'order']
    
    fieldsets = (
        ('Question', {
            'fields': ('quiz', 'question_text', 'question_type', 'points', 'order')
        }),
        ('Correction et aide', {
            'fields': ('explanation', 'text_answer_keywords'),
            'description': 'Pour les questions texte libre, séparez les mots-clés par des virgules'
        }),
    )
    
    def question_text_short(self, obj):
        return obj.question_text[:50] + "..." if len(obj.question_text) > 50 else obj.question_text
    question_text_short.short_description = "Question"
    
    def has_correct_answers(self, obj):
        return obj.answers.filter(is_correct=True).exists()
    has_correct_answers.boolean = True
    has_correct_answers.short_description = "A des bonnes réponses"


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['question_short', 'answer_text', 'is_correct', 'order']
    list_filter = ['is_correct', 'question__question_type', 'question__quiz']
    search_fields = ['answer_text', 'question__question_text']
    ordering = ['question', 'order']
    
    def question_short(self, obj):
        return f"{obj.question.quiz.title} - Q{obj.question.order + 1}"
    question_short.short_description = "Question"


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'attempt_number', 'status', 'score', 'is_passed', 'started_at', 'completed_at']
    list_filter = ['status', 'is_passed', 'quiz', 'started_at']
    search_fields = ['user__username', 'user__email', 'quiz__title']
    readonly_fields = ['attempt_number', 'score', 'is_passed', 'started_at', 'completed_at']
    ordering = ['-started_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('user', 'quiz', 'enrollment', 'attempt_number', 'status')
        }),
        ('Résultats', {
            'fields': ('score', 'total_points', 'earned_points', 'is_passed')
        }),
        ('Temps', {
            'fields': ('started_at', 'completed_at', 'time_spent_seconds')
        }),
    )


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ['attempt_user', 'question_short', 'is_correct', 'points_earned', 'answered_at']
    list_filter = ['is_correct', 'question__question_type', 'attempt__quiz']
    search_fields = ['attempt__user__username', 'question__question_text', 'text_answer']
    readonly_fields = ['is_correct', 'points_earned', 'answered_at']
    ordering = ['-answered_at']
    
    def attempt_user(self, obj):
        return f"{obj.attempt.user.username} - Tentative {obj.attempt.attempt_number}"
    attempt_user.short_description = "Utilisateur"
    
    def question_short(self, obj):
        return f"{obj.question.quiz.title} - Q{obj.question.order + 1}"
    question_short.short_description = "Question"