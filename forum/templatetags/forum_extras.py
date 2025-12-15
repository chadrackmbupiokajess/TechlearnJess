from django import template
from django.utils import timezone
from django.utils.timesince import timesince

register = template.Library()

@register.filter
def human_timesince(date):
    """
    Retourne une chaîne de caractères représentant le temps écoulé depuis une date,
    avec plus de précision que le filtre `timesince` de Django.
    """
    now = timezone.now()
    delta = now - date

    if delta.days > 365:
        years = delta.days // 365
        return f"il y a {years} an{'s' if years > 1 else ''}"
    if delta.days > 30:
        months = delta.days // 30
        return f"il y a {months} mois"
    if delta.days > 0:
        return f"il y a {delta.days} jour{'s' if delta.days > 1 else ''}"
    if delta.seconds > 3600:
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        if minutes > 0:
            return f"il y a {hours} heure{'s' if hours > 1 else ''}, {minutes} minute{'s' if minutes > 1 else ''}"
        return f"il y a {hours} heure{'s' if hours > 1 else ''}"
    if delta.seconds > 60:
        minutes = delta.seconds // 60
        return f"il y a {minutes} minute{'s' if minutes > 1 else ''}"
    
    return "à l'instant"