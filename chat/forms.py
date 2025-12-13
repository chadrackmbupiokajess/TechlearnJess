from django import forms
from .models import ChatRoom

class ChatRoomForm(forms.ModelForm):
    class Meta:
        model = ChatRoom
        fields = ['nom', 'description', 'est_prive']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white', 'placeholder': 'Ex: Développement Web'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white', 'rows': '3', 'placeholder': 'Décrivez le sujet de discussion...'}),
            'est_prive': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-indigo-600 focus:ring-indigo-500'}),
        }
