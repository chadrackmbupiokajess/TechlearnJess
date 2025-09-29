from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='list'),
    path('mes-cours/', views.my_courses, name='my_courses'),
    path('categorie/<slug:slug>/', views.category_courses, name='category'),
    path('<slug:slug>/', views.course_detail, name='detail'),
    path('<slug:slug>/inscription/', views.enroll_course, name='enroll'),
    path('<slug:slug>/apprendre/', views.learn_course, name='learn'),
    path('<slug:slug>/apprendre/<slug:lesson_slug>/', views.learn_course, name='learn_lesson'),
    path('<slug:slug>/lecon/<slug:lesson_slug>/terminer/', views.complete_lesson, name='complete_lesson'),
    path('<slug:slug>/avis/', views.add_review, name='add_review'),
    
    # URLs pour les quiz
    path('<slug:course_slug>/lecon/<slug:lesson_slug>/quiz/data/', views.get_quiz_data, name='quiz_data'),
    path('<slug:course_slug>/lecon/<slug:lesson_slug>/quiz/start/', views.start_quiz, name='start_quiz'),
    path('quiz/attempt/<int:attempt_id>/question/<int:question_id>/answer/', views.submit_answer, name='submit_answer'),
    path('quiz/attempt/<int:attempt_id>/finish/', views.finish_quiz, name='finish_quiz'),
]