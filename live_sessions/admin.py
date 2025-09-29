from django.contrib import admin
from django.utils import timezone
from .models import LiveSession, SessionParticipant, SessionQuestion, SessionResource


class SessionParticipantInline(admin.TabularInline):
    model = SessionParticipant
    extra = 0
    readonly_fields = ['joined_at', 'left_at', 'attendance_duration']


class SessionQuestionInline(admin.TabularInline):
    model = SessionQuestion
    extra = 0
    readonly_fields = ['asked_at', 'answered_at']


class SessionResourceInline(admin.TabularInline):
    model = SessionResource
    extra = 0
    readonly_fields = ['shared_at']


@admin.register(LiveSession)
class LiveSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'start_time', 'end_time', 'status', 'participants_count', 'max_participants']
    list_filter = ['status', 'start_time', 'is_public', 'requires_enrollment', 'is_recorded']
    search_fields = ['title', 'description', 'instructor__username']
    readonly_fields = ['session_id', 'created_at', 'updated_at', 'participants_count']
    list_editable = ['status']
    date_hierarchy = 'start_time'
    inlines = [SessionParticipantInline, SessionQuestionInline, SessionResourceInline]
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'description', 'instructor', 'course', 'session_id')
        }),
        ('Planification', {
            'fields': ('start_time', 'end_time', 'timezone', 'status')
        }),
        ('Participants', {
            'fields': ('max_participants', 'participants_count')
        }),
        ('Liens et ressources', {
            'fields': ('meeting_url', 'recording_url', 'presentation_file')
        }),
        ('Paramètres', {
            'fields': ('is_recorded', 'is_public', 'requires_enrollment')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['start_sessions', 'end_sessions', 'cancel_sessions']
    
    def start_sessions(self, request, queryset):
        for session in queryset:
            session.start_session()
        self.message_user(request, f"{queryset.count()} sessions démarrées.")
    start_sessions.short_description = "Démarrer les sessions sélectionnées"
    
    def end_sessions(self, request, queryset):
        for session in queryset:
            session.end_session()
        self.message_user(request, f"{queryset.count()} sessions terminées.")
    end_sessions.short_description = "Terminer les sessions sélectionnées"
    
    def cancel_sessions(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, f"{queryset.count()} sessions annulées.")
    cancel_sessions.short_description = "Annuler les sessions sélectionnées"


@admin.register(SessionParticipant)
class SessionParticipantAdmin(admin.ModelAdmin):
    list_display = ['user', 'session', 'joined_at', 'left_at', 'is_present', 'attendance_duration']
    list_filter = ['is_present', 'joined_at', 'session__status']
    search_fields = ['user__username', 'session__title']
    readonly_fields = ['joined_at', 'left_at', 'attendance_duration']


@admin.register(SessionQuestion)
class SessionQuestionAdmin(admin.ModelAdmin):
    list_display = ['user', 'session', 'question_short', 'is_answered', 'is_public', 'asked_at']
    list_filter = ['is_answered', 'is_public', 'asked_at']
    search_fields = ['user__username', 'session__title', 'question']
    readonly_fields = ['asked_at', 'answered_at']
    list_editable = ['is_answered', 'is_public']
    
    def question_short(self, obj):
        return obj.question[:50] + "..." if len(obj.question) > 50 else obj.question
    question_short.short_description = 'Question'


@admin.register(SessionResource)
class SessionResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'session', 'shared_at']
    list_filter = ['shared_at']
    search_fields = ['title', 'session__title']
    readonly_fields = ['shared_at']