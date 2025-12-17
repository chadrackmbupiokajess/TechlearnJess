import pytz
from django import forms
from .models import LiveSession

class LiveSessionForm(forms.ModelForm):
    # Créer une liste de tuples (valeur, libellé) pour les fuseaux horaires
    TIMEZONE_CHOICES = [(tz, tz) for tz in pytz.common_timezones]

    # Redéfinir le champ 'timezone' comme un ChoiceField
    timezone = forms.ChoiceField(
        choices=TIMEZONE_CHOICES,
        label="Fuseau horaire",
        help_text="Sélectionnez le fuseau horaire de la session."
    )

    class Meta:
        model = LiveSession
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si on édite une session existante, s'assurer que sa valeur est bien sélectionnée
        if self.instance and self.instance.pk and self.instance.timezone:
            self.fields['timezone'].initial = self.instance.timezone
        # Sinon, pour une nouvelle session, on peut garder la valeur par défaut du modèle
        else:
            self.fields['timezone'].initial = 'Africa/Kinshasa'
