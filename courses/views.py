from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from .models import Course, Category, Enrollment, Lesson, LessonProgress, Review, Quiz, Question, Answer, QuizAttempt, StudentAnswer
from .forms import ReviewForm


def course_list(request):
    """Liste des cours"""
    courses = Course.objects.filter(is_published=True).select_related('category', 'instructor')
    categories = Category.objects.filter(is_active=True)
    
    # Filtres
    category_slug = request.GET.get('category')
    difficulty = request.GET.get('difficulty')
    is_free = request.GET.get('free')
    search = request.GET.get('search')
    sort_by = request.GET.get('sort', 'newest')
    
    if category_slug:
        courses = courses.filter(category__slug=category_slug)
    
    if difficulty:
        courses = courses.filter(difficulty=difficulty)
    
    if is_free == 'true':
        courses = courses.filter(is_free=True)
    
    if search:
        courses = courses.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(short_description__icontains=search)
        )
    
    # Tri
    if sort_by == 'newest':
        courses = courses.order_by('-created_at')
    elif sort_by == 'oldest':
        courses = courses.order_by('created_at')
    elif sort_by == 'popular':
        courses = courses.annotate(enrollment_count=Count('enrollments')).order_by('-enrollment_count')
    elif sort_by == 'rating':
        courses = courses.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
    elif sort_by == 'price_low':
        courses = courses.order_by('price')
    elif sort_by == 'price_high':
        courses = courses.order_by('-price')
    
    # Pagination
    paginator = Paginator(courses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category_slug,
        'current_difficulty': difficulty,
        'current_free': is_free,
        'current_search': search,
        'current_sort': sort_by,
        'difficulty_choices': Course.DIFFICULTY_CHOICES,
    }
    
    return render(request, 'courses/course_list.html', context)


def course_detail(request, slug):
    """Détail d'un cours"""
    course = get_object_or_404(Course, slug=slug, is_published=True)
    lessons = course.lessons.filter(is_published=True).order_by('order')
    reviews = course.reviews.filter(is_approved=True).order_by('-created_at')[:5]
    
    # Vérifier si l'utilisateur est inscrit
    is_enrolled = False
    enrollment = None
    if request.user.is_authenticated:
        try:
            enrollment = Enrollment.objects.get(user=request.user, course=course)
            is_enrolled = True
        except Enrollment.DoesNotExist:
            pass
    
    # Cours similaires
    similar_courses = Course.objects.filter(
        category=course.category,
        is_published=True
    ).exclude(id=course.id)[:4]
    
    context = {
        'course': course,
        'lessons': lessons,
        'reviews': reviews,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
        'similar_courses': similar_courses,
        'review_form': ReviewForm() if request.user.is_authenticated else None,
    }
    
    return render(request, 'courses/course_detail.html', context)


@login_required
@require_http_methods(["POST"])
def enroll_course(request, slug):
    """Inscription à un cours"""
    course = get_object_or_404(Course, slug=slug, is_published=True)
    
    # Vérifier si déjà inscrit
    if Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.warning(request, 'Vous êtes déjà inscrit à ce cours.')
        return redirect('courses:detail', slug=slug)
    
    # Pour les cours payants, vérifier le paiement (à implémenter)
    if not course.is_free:
        # Rediriger vers la page de paiement
        messages.info(request, 'Veuillez procéder au paiement pour accéder à ce cours.')
        return redirect('payments:checkout', course_slug=slug)
    
    # Créer l'inscription
    enrollment = Enrollment.objects.create(user=request.user, course=course)
    messages.success(request, f'Vous êtes maintenant inscrit au cours "{course.title}"!')
    
    return redirect('courses:learn', slug=slug)


@login_required
def learn_course(request, slug, lesson_slug=None):
    """Interface d'apprentissage"""
    course = get_object_or_404(Course, slug=slug, is_published=True)
    
    # Vérifier l'inscription
    try:
        enrollment = Enrollment.objects.get(user=request.user, course=course)
    except Enrollment.DoesNotExist:
        messages.error(request, 'Vous devez être inscrit à ce cours pour y accéder.')
        return redirect('courses:detail', slug=slug)
    
    lessons = course.lessons.filter(is_published=True).order_by('order')
    
    # Vérifier qu'il y a des leçons
    if not lessons.exists():
        messages.warning(request, 'Ce cours ne contient pas encore de leçons.')
        return redirect('courses:detail', slug=slug)
    
    # Leçon actuelle
    if lesson_slug:
        current_lesson = get_object_or_404(lessons, slug=lesson_slug)
    else:
        # Première leçon non terminée ou première leçon
        completed_lessons = LessonProgress.objects.filter(
            enrollment=enrollment,
            is_completed=True
        ).values_list('lesson_id', flat=True)
        
        next_lesson = lessons.exclude(id__in=completed_lessons).first()
        current_lesson = next_lesson or lessons.first()
    
    # Progression de la leçon actuelle (seulement si current_lesson existe)
    lesson_progress = None
    if current_lesson:
        lesson_progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=current_lesson
        )
    
    # Toutes les progressions pour la sidebar
    all_progress = LessonProgress.objects.filter(enrollment=enrollment)
    progress_dict = {p.lesson_id: p for p in all_progress}
    
    context = {
        'course': course,
        'enrollment': enrollment,
        'lessons': lessons,
        'current_lesson': current_lesson,
        'lesson_progress': lesson_progress,
        'progress_dict': progress_dict,
    }
    
    return render(request, 'courses/learn.html', context)


@login_required
@require_http_methods(["POST"])
def complete_lesson(request, slug, lesson_slug):
    """Marquer une leçon comme terminée"""
    course = get_object_or_404(Course, slug=slug)
    lesson = get_object_or_404(Lesson, course=course, slug=lesson_slug)
    
    try:
        enrollment = Enrollment.objects.get(user=request.user, course=course)
    except Enrollment.DoesNotExist:
        return JsonResponse({'error': 'Non inscrit'}, status=403)
    
    progress, created = LessonProgress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson
    )
    
    if not progress.is_completed:
        progress.is_completed = True
        progress.completed_at = timezone.now()
        progress.save()
        
        # Mettre à jour la progression du cours
        enrollment.update_progress()
        
        return JsonResponse({
            'success': True,
            'message': 'Leçon terminée!',
            'course_progress': enrollment.progress_percentage
        })
    
    return JsonResponse({'success': True, 'message': 'Déjà terminée'})


@login_required
def my_courses(request):
    """Mes cours"""
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
    
    # Calculer les statistiques
    total_enrollments = enrollments.count()
    completed_count = enrollments.filter(is_completed=True).count()
    in_progress_count = total_enrollments - completed_count
    
    # Filtres
    status = request.GET.get('status', 'all')
    if status == 'completed':
        enrollments = enrollments.filter(is_completed=True)
    elif status == 'in_progress':
        enrollments = enrollments.filter(is_completed=False)
    
    context = {
        'enrollments': enrollments,
        'current_status': status,
        'total_enrollments': total_enrollments,
        'completed_count': completed_count,
        'in_progress_count': in_progress_count,
    }
    
    return render(request, 'courses/my_courses.html', context)


@login_required
@require_http_methods(["POST"])
def add_review(request, slug):
    """Ajouter un avis"""
    course = get_object_or_404(Course, slug=slug)
    
    # Vérifier si inscrit
    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.error(request, 'Vous devez être inscrit pour laisser un avis.')
        return redirect('courses:detail', slug=slug)
    
    # Vérifier si déjà un avis
    if Review.objects.filter(user=request.user, course=course).exists():
        messages.warning(request, 'Vous avez déjà laissé un avis pour ce cours.')
        return redirect('courses:detail', slug=slug)
    
    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.user = request.user
        review.course = course
        review.save()
        messages.success(request, 'Votre avis a été ajouté avec succès!')
    else:
        messages.error(request, 'Erreur dans le formulaire.')
    
    return redirect('courses:detail', slug=slug)


def category_courses(request, slug):
    """Cours par catégorie"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    courses = Course.objects.filter(category=category, is_published=True)
    
    # Pagination
    paginator = Paginator(courses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    
    return render(request, 'courses/category_courses.html', context)


@login_required
@require_http_methods(["POST"])
def start_quiz(request, course_slug, lesson_slug):
    """Démarrer un nouveau quiz"""
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, course=course, slug=lesson_slug)
    
    # Vérifier l'inscription
    try:
        enrollment = Enrollment.objects.get(user=request.user, course=course)
    except Enrollment.DoesNotExist:
        return JsonResponse({'error': 'Non inscrit au cours'}, status=403)
    
    # Vérifier qu'il y a un quiz
    try:
        quiz = lesson.quiz
    except Quiz.DoesNotExist:
        return JsonResponse({'error': 'Pas de quiz pour cette leçon'}, status=404)
    
    # Vérifier le nombre de tentatives
    attempts_count = QuizAttempt.objects.filter(user=request.user, quiz=quiz).count()
    if attempts_count >= quiz.max_attempts:
        return JsonResponse({'error': f'Nombre maximum de tentatives atteint ({quiz.max_attempts})'}, status=400)
    
    # Créer une nouvelle tentative
    attempt = QuizAttempt.objects.create(
        user=request.user,
        quiz=quiz,
        enrollment=enrollment,
        total_points=sum(q.points for q in quiz.questions.all())
    )
    
    return JsonResponse({
        'success': True,
        'attempt_id': attempt.id,
        'questions': [
            {
                'id': q.id,
                'text': q.question_text,
                'type': q.question_type,
                'points': q.points,
                'order': q.order,
                'answers': [
                    {
                        'id': a.id,
                        'text': a.answer_text,
                        'order': a.order
                    } for a in q.answers.all().order_by('order')
                ] if q.question_type in ['multiple_choice', 'true_false'] else []
            } for q in quiz.questions.all().order_by('order')
        ],
        'time_limit_seconds': quiz.time_limit_minutes * 60 if quiz.time_limit_minutes else None
    })


@login_required
@require_http_methods(["POST"])
def submit_answer(request, attempt_id, question_id):
    """Soumettre une réponse à une question"""
    import json
    
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user, status='in_progress')
    question = get_object_or_404(Question, id=question_id, quiz=attempt.quiz)
    
    data = json.loads(request.body)
    
    # Créer ou mettre à jour la réponse de l'étudiant
    student_answer, created = StudentAnswer.objects.get_or_create(
        attempt=attempt,
        question=question,
        defaults={'time_spent_seconds': data.get('time_spent', 0)}
    )
    
    if not created:
        student_answer.time_spent_seconds = data.get('time_spent', 0)
    
    # Traiter la réponse selon le type de question
    if question.question_type == 'text':
        student_answer.text_answer = data.get('text_answer', '')
    else:
        # Choix multiple ou vrai/faux
        answer_ids = data.get('answer_ids', [])
        if not isinstance(answer_ids, list):
            answer_ids = [answer_ids]
        
        # Nettoyer les réponses existantes
        student_answer.selected_answers.clear()
        
        # Ajouter les nouvelles réponses
        for answer_id in answer_ids:
            try:
                answer = Answer.objects.get(id=answer_id, question=question)
                student_answer.selected_answers.add(answer)
            except Answer.DoesNotExist:
                continue
    
    # Évaluer la réponse
    student_answer.evaluate_answer()
    
    # Préparer la réponse avec correction
    response_data = {
        'success': True,
        'is_correct': student_answer.is_correct,
        'points_earned': student_answer.points_earned,
        'points_possible': question.points,
        'explanation': question.explanation
    }
    
    # Ajouter les bonnes réponses pour feedback
    if question.question_type in ['multiple_choice', 'true_false']:
        correct_answers = question.get_correct_answers()
        response_data['correct_answers'] = [
            {
                'id': a.id,
                'text': a.answer_text
            } for a in correct_answers
        ]
    
    return JsonResponse(response_data)


@login_required
@require_http_methods(["POST"])
def finish_quiz(request, attempt_id):
    """Terminer un quiz"""
    import json
    
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user, status='in_progress')
    
    data = json.loads(request.body)
    reason = data.get('reason', 'completed')  # 'completed' ou 'time_expired'
    
    # Calculer les points totaux obtenus
    total_earned = sum(sa.points_earned for sa in attempt.student_answers.all())
    attempt.earned_points = total_earned
    attempt.time_spent_seconds = data.get('total_time_spent', 0)
    
    # Marquer comme terminé
    attempt.status = 'time_expired' if reason == 'time_expired' else 'completed'
    attempt.completed_at = timezone.now()
    attempt.save()  # Le score sera calculé automatiquement
    
    # Si réussi, marquer la leçon comme terminée
    if attempt.is_passed:
        lesson_progress, created = LessonProgress.objects.get_or_create(
            enrollment=attempt.enrollment,
            lesson=attempt.quiz.lesson
        )
        if not lesson_progress.is_completed:
            lesson_progress.is_completed = True
            lesson_progress.completed_at = timezone.now()
            lesson_progress.save()
            
            # Mettre à jour la progression du cours
            attempt.enrollment.update_progress()
    
    return JsonResponse({
        'success': True,
        'score': float(attempt.score),
        'is_passed': attempt.is_passed,
        'passing_score': attempt.quiz.passing_score,
        'earned_points': attempt.earned_points,
        'total_points': attempt.total_points,
        'attempt_number': attempt.attempt_number,
        'can_retake': QuizAttempt.objects.filter(
            user=request.user, 
            quiz=attempt.quiz
        ).count() < attempt.quiz.max_attempts
    })


@login_required
def get_quiz_data(request, course_slug, lesson_slug):
    """Récupérer les données d'un quiz pour l'affichage"""
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, course=course, slug=lesson_slug)
    
    # Vérifier l'inscription
    try:
        enrollment = Enrollment.objects.get(user=request.user, course=course)
    except Enrollment.DoesNotExist:
        return JsonResponse({'error': 'Non inscrit au cours'}, status=403)
    
    # Vérifier qu'il y a un quiz
    try:
        quiz = lesson.quiz
    except Quiz.DoesNotExist:
        return JsonResponse({'error': 'Pas de quiz pour cette leçon'}, status=404)
    
    # Récupérer les tentatives précédentes
    attempts = QuizAttempt.objects.filter(user=request.user, quiz=quiz).order_by('-started_at')
    
    return JsonResponse({
        'quiz': {
            'id': quiz.id,
            'title': quiz.title,
            'description': quiz.description,
            'passing_score': quiz.passing_score,
            'max_attempts': quiz.max_attempts,
            'time_limit_minutes': quiz.time_limit_minutes,
            'questions_count': quiz.questions.count(),
            'total_points': sum(q.points for q in quiz.questions.all())
        },
        'attempts': [
            {
                'id': attempt.id,
                'attempt_number': attempt.attempt_number,
                'status': attempt.status,
                'score': float(attempt.score),
                'is_passed': attempt.is_passed,
                'started_at': attempt.started_at.isoformat(),
                'completed_at': attempt.completed_at.isoformat() if attempt.completed_at else None
            } for attempt in attempts
        ],
        'can_start_new': attempts.count() < quiz.max_attempts,
        'remaining_attempts': quiz.max_attempts - attempts.count()
    })