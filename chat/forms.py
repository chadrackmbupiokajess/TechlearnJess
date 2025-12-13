from django import forms
from django.contrib.auth.models import User
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


class InviteMembersForm(forms.Form):
    """Formulaire pour inviter des membres à un salon de chat."""
    users_to_invite = forms.ModelMultipleChoiceField(
        queryset=User.objects.all().order_by('username'),
        widget=forms.CheckboxSelectMultiple,
        label="Sélectionnez les membres à inviter"
    )

    def __init__(self, *args, **kwargs):
        self.chatroom = kwargs.pop('chatroom', None)
        super().__init__(*args, **kwargs)
        if self.chatroom:
            # Exclure les utilisateurs déjà membres du salon
            self.fields['users_to_invite'].queryset = User.objects.exclude(
                id__in=self.chatroom.participants.all().values_list('id', flat=True)
            ).order_by('username')
        
        # Appliquer des classes Tailwind CSS aux widgets
        self.fields['users_to_invite'].widget.attrs.update({
            'class': 'form-checkbox h-5 w-5 text-indigo-600'
        })
        # Pour le label, on peut le styliser directement dans le template ou via un custom widget
