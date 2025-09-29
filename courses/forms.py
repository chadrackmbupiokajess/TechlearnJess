from django import forms
from .models import Review, Course


class ReviewForm(forms.ModelForm):
    """Formulaire d'avis sur un cours"""
    
    class Meta:
        model = Review
        fields = ['rating', 'title', 'content']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f'{i} étoile{"s" if i > 1 else ""}') for i in range(1, 6)],
                attrs={
                    'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent'
                }
            ),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent',
                'placeholder': 'Titre de votre avis'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Partagez votre expérience avec ce cours...'
            }),
        }
        labels = {
            'rating': 'Note',
            'title': 'Titre',
            'content': 'Commentaire',
        }


class CourseSearchForm(forms.Form):
    """Formulaire de recherche de cours"""
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent',
            'placeholder': 'Rechercher un cours...'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=None,  # Sera défini dans __init__
        required=False,
        empty_label="Toutes les catégories",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent'
        })
    )
    
    difficulty = forms.ChoiceField(
        choices=[('', 'Tous les niveaux')] + Course.DIFFICULTY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent'
        })
    )
    
    is_free = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500'
        }),
        label='Cours gratuits uniquement'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Category
        self.fields['category'].queryset = Category.objects.filter(is_active=True)