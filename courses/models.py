from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
import uuid


class Category(models.Model):
    """Catégories de cours"""
    name = models.CharField(max_length=100, verbose_name="Nom")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Description")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Icône (classe CSS)")
    color = models.CharField(max_length=7, default="#3B82F6", verbose_name="Couleur")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    order = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Course(models.Model):
    """Modèle de cours"""
    DIFFICULTY_CHOICES = [
        ('beginner', 'Débutant'),
        ('intermediate', 'Intermédiaire'),
        ('advanced', 'Avancé'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
        ('archived', 'Archivé'),
    ]

    title = models.CharField(max_length=200, verbose_name="Titre")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    description = models.TextField(verbose_name="Description")
    short_description = models.CharField(max_length=300, verbose_name="Description courte")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Catégorie")
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Formateur")
    
    # Contenu
    thumbnail = models.ImageField(upload_to='courses/thumbnails/', verbose_name="Miniature")
    video_intro = models.URLField(blank=True, verbose_name="Vidéo d'introduction")
    
    # Métadonnées
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner', verbose_name="Difficulté")
    duration_hours = models.PositiveIntegerField(verbose_name="Durée (heures)")
    language = models.CharField(max_length=10, default='fr', verbose_name="Langue")
    
    # Prix et accès
    is_free = models.BooleanField(default=False, verbose_name="Gratuit")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Prix (USD)")
    
    # Statut
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Statut")
    is_published = models.BooleanField(default=False, verbose_name="Publié")
    is_featured = models.BooleanField(default=False, verbose_name="Mis en avant")
    
    # Prérequis et objectifs
    prerequisites = models.TextField(blank=True, verbose_name="Prérequis")
    learning_objectives = models.TextField(verbose_name="Objectifs d'apprentissage")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cours"
        verbose_name_plural = "Cours"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('courses:detail', kwargs={'slug': self.slug})

    @property
    def total_lessons(self):
        return self.lessons.count()

    @property
    def total_enrollments(self):
        return self.enrollments.count()

    @property
    def average_rating(self):
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)
        return 0

    @property
    def total_reviews(self):
        return self.reviews.filter(is_approved=True).count()


class Lesson(models.Model):
    """Leçons d'un cours"""
    LESSON_TYPES = [
        ('video', 'Vidéo'),
        ('text', 'Texte'),
        ('quiz', 'Quiz'),
        ('assignment', 'Devoir'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name="Cours")
    title = models.CharField(max_length=200, verbose_name="Titre")
    slug = models.SlugField(verbose_name="Slug")
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPES, default='video', verbose_name="Type")
    
    # Contenu
    content = models.TextField(blank=True, verbose_name="Contenu texte")
    video_url = models.URLField(blank=True, verbose_name="URL vidéo")
    duration_minutes = models.PositiveIntegerField(default=0, verbose_name="Durée (minutes)")
    
    # Ressources
    attachments = models.FileField(upload_to='courses/attachments/', blank=True, verbose_name="Fichiers joints")
    
    # Ordre et accès
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    is_preview = models.BooleanField(default=False, verbose_name="Aperçu gratuit")
    is_published = models.BooleanField(default=True, verbose_name="Publié")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Leçon"
        verbose_name_plural = "Leçons"
        ordering = ['course', 'order']
        unique_together = ['course', 'slug']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Enrollment(models.Model):
    """Inscriptions aux cours"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments', verbose_name="Cours")
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")
    is_completed = models.BooleanField(default=False, verbose_name="Terminé")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de fin")
    progress_percentage = models.PositiveIntegerField(default=0, verbose_name="Progression (%)")
    
    class Meta:
        verbose_name = "Inscription"
        verbose_name_plural = "Inscriptions"
        unique_together = ['user', 'course']
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"

    def update_progress(self):
        """Mettre à jour la progression"""
        total_lessons = self.course.lessons.count()
        if total_lessons > 0:
            completed_lessons = LessonProgress.objects.filter(
                enrollment=self,
                is_completed=True
            ).count()
            self.progress_percentage = int((completed_lessons / total_lessons) * 100)
            
            if self.progress_percentage == 100 and not self.is_completed:
                self.is_completed = True
                from django.utils import timezone
                self.completed_at = timezone.now()
            
            self.save()


class LessonProgress(models.Model):
    """Progression dans les leçons"""
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, verbose_name="Inscription")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name="Leçon")
    is_completed = models.BooleanField(default=False, verbose_name="Terminé")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de fin")
    time_spent_minutes = models.PositiveIntegerField(default=0, verbose_name="Temps passé (minutes)")
    
    class Meta:
        verbose_name = "Progression de leçon"
        verbose_name_plural = "Progressions de leçons"
        unique_together = ['enrollment', 'lesson']

    def __str__(self):
        return f"{self.enrollment.user.username} - {self.lesson.title}"


class Review(models.Model):
    """Avis sur les cours"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews', verbose_name="Cours")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name="Note")
    title = models.CharField(max_length=100, verbose_name="Titre")
    content = models.TextField(verbose_name="Commentaire")
    is_approved = models.BooleanField(default=True, verbose_name="Approuvé")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        unique_together = ['course', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.course.title} - {self.user.username} ({self.rating}/5)"


class Quiz(models.Model):
    """Quiz associés aux leçons"""
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, verbose_name="Leçon")
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    passing_score = models.PositiveIntegerField(default=70, verbose_name="Score de réussite (%)")
    time_limit_minutes = models.PositiveIntegerField(null=True, blank=True, verbose_name="Limite de temps (minutes)")
    max_attempts = models.PositiveIntegerField(default=3, verbose_name="Nombre max de tentatives")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quiz"

    def __str__(self):
        return self.title


class Question(models.Model):
    """Questions de quiz"""
    QUESTION_TYPES = [
        ('multiple_choice', 'Choix multiple'),
        ('true_false', 'Vrai/Faux'),
        ('text', 'Texte libre'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions', verbose_name="Quiz")
    question_text = models.TextField(verbose_name="Question")
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, verbose_name="Type")
    points = models.PositiveIntegerField(default=1, verbose_name="Points")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    explanation = models.TextField(blank=True, verbose_name="Explication de la réponse")
    
    # Pour les questions texte libre
    text_answer_keywords = models.TextField(blank=True, verbose_name="Mots-clés attendus (séparés par des virgules)")
    
    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ['quiz', 'order']

    def __str__(self):
        return f"{self.quiz.title} - Q{self.order + 1}: {self.question_text[:50]}..."
    
    def get_correct_answers(self):
        """Retourne les bonnes réponses pour cette question"""
        return self.answers.filter(is_correct=True)


class Answer(models.Model):
    """Réponses possibles aux questions"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name="Question")
    answer_text = models.CharField(max_length=200, verbose_name="Réponse")
    is_correct = models.BooleanField(default=False, verbose_name="Réponse correcte")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")

    class Meta:
        verbose_name = "Réponse"
        verbose_name_plural = "Réponses"
        ordering = ['question', 'order']

    def __str__(self):
        return f"{self.question} - {self.answer_text}"


class QuizAttempt(models.Model):
    """Tentatives de quiz par les étudiants"""
    STATUS_CHOICES = [
        ('in_progress', 'En cours'),
        ('completed', 'Terminé'),
        ('time_expired', 'Temps expiré'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts', verbose_name="Quiz")
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, verbose_name="Inscription")
    
    # Informations de la tentative
    attempt_number = models.PositiveIntegerField(verbose_name="Numéro de tentative")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress', verbose_name="Statut")
    
    # Scores et résultats
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Score (%)")
    total_points = models.PositiveIntegerField(default=0, verbose_name="Points totaux possibles")
    earned_points = models.PositiveIntegerField(default=0, verbose_name="Points obtenus")
    
    # Temps
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Commencé à")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Terminé à")
    time_spent_seconds = models.PositiveIntegerField(default=0, verbose_name="Temps passé (secondes)")
    
    # Résultats
    is_passed = models.BooleanField(default=False, verbose_name="Réussi")
    
    class Meta:
        verbose_name = "Tentative de quiz"
        verbose_name_plural = "Tentatives de quiz"
        unique_together = ['user', 'quiz', 'attempt_number']
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - Tentative {self.attempt_number}"
    
    def calculate_score(self):
        """Calcule le score basé sur les réponses"""
        if self.total_points == 0:
            return 0
        return (self.earned_points / self.total_points) * 100
    
    def save(self, *args, **kwargs):
        if not self.attempt_number:
            # Calculer le numéro de tentative
            last_attempt = QuizAttempt.objects.filter(
                user=self.user, 
                quiz=self.quiz
            ).order_by('-attempt_number').first()
            self.attempt_number = (last_attempt.attempt_number + 1) if last_attempt else 1
        
        # Calculer le score
        if self.total_points > 0:
            self.score = self.calculate_score()
            self.is_passed = self.score >= self.quiz.passing_score
        
        super().save(*args, **kwargs)


class StudentAnswer(models.Model):
    """Réponses données par les étudiants"""
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='student_answers', verbose_name="Tentative")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="Question")
    
    # Réponses selon le type de question
    selected_answers = models.ManyToManyField(Answer, blank=True, verbose_name="Réponses sélectionnées")
    text_answer = models.TextField(blank=True, verbose_name="Réponse texte")
    
    # Résultats
    is_correct = models.BooleanField(default=False, verbose_name="Réponse correcte")
    points_earned = models.PositiveIntegerField(default=0, verbose_name="Points obtenus")
    
    # Temps
    answered_at = models.DateTimeField(auto_now_add=True, verbose_name="Répondu à")
    time_spent_seconds = models.PositiveIntegerField(default=0, verbose_name="Temps passé sur cette question")
    
    class Meta:
        verbose_name = "Réponse d'étudiant"
        verbose_name_plural = "Réponses d'étudiants"
        unique_together = ['attempt', 'question']
        ordering = ['question__order']
    
    def __str__(self):
        return f"{self.attempt.user.username} - {self.question}"
    
    def evaluate_answer(self):
        """Évalue la réponse et met à jour is_correct et points_earned"""
        question = self.question
        
        if question.question_type == 'multiple_choice':
            # Choix multiple
            correct_answers = set(question.get_correct_answers())
            selected_answers = set(self.selected_answers.all())
            
            if correct_answers == selected_answers:
                self.is_correct = True
                self.points_earned = question.points
            else:
                self.is_correct = False
                self.points_earned = 0
                
        elif question.question_type == 'true_false':
            # Vrai/Faux
            correct_answer = question.get_correct_answers().first()
            selected_answer = self.selected_answers.first()
            
            if correct_answer and selected_answer and correct_answer == selected_answer:
                self.is_correct = True
                self.points_earned = question.points
            else:
                self.is_correct = False
                self.points_earned = 0
                
        elif question.question_type == 'text':
            # Texte libre
            if question.text_answer_keywords and self.text_answer:
                keywords = [kw.strip().lower() for kw in question.text_answer_keywords.split(',')]
                user_answer = self.text_answer.lower()
                
                # Vérifier si au moins un mot-clé est présent
                found_keywords = [kw for kw in keywords if kw in user_answer]
                
                if found_keywords:
                    # Score partiel basé sur le nombre de mots-clés trouvés
                    score_ratio = len(found_keywords) / len(keywords)
                    self.points_earned = int(question.points * score_ratio)
                    self.is_correct = score_ratio >= 0.5  # 50% des mots-clés minimum
                else:
                    self.is_correct = False
                    self.points_earned = 0
            else:
                # Pas de mots-clés définis, donner des points par défaut si réponse non vide
                if self.text_answer.strip():
                    self.is_correct = True
                    self.points_earned = question.points
                else:
                    self.is_correct = False
                    self.points_earned = 0
        
        self.save()