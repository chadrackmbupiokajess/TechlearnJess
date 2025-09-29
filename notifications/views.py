from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.contrib import messages

from .models import Notification, NotificationSettings


@login_required
def notification_list(request):
    """Liste des notifications"""
    notifications = Notification.objects.filter(user=request.user)
    
    # Filtres
    filter_type = request.GET.get('type', 'all')
    if filter_type == 'unread':
        notifications = notifications.filter(is_read=False)
    elif filter_type != 'all':
        notifications = notifications.filter(notification_type=filter_type)
    
    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Compter les non lues
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    
    context = {
        'page_obj': page_obj,
        'unread_count': unread_count,
        'current_filter': filter_type,
        'notification_types': Notification.NOTIFICATION_TYPES,
    }
    
    return render(request, 'notifications/list.html', context)


@login_required
@require_http_methods(["POST"])
def mark_as_read(request, notification_id):
    """Marquer une notification comme lue"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def mark_all_as_read(request):
    """Marquer toutes les notifications comme lues"""
    Notification.objects.filter(user=request.user, is_read=False).update(
        is_read=True,
        read_at=timezone.now()
    )
    
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def delete_notification(request, notification_id):
    """Supprimer une notification"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    
    return JsonResponse({'success': True})


@login_required
def notification_settings(request):
    """Paramètres de notification"""
    settings, created = NotificationSettings.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Mettre à jour les paramètres
        for field in NotificationSettings._meta.fields:
            if field.name.startswith(('email_', 'push_')) and field.name in request.POST:
                setattr(settings, field.name, True)
            elif field.name.startswith(('email_', 'push_')):
                setattr(settings, field.name, False)
        
        settings.save()
        messages.success(request, 'Vos paramètres de notification ont été mis à jour.')
        return redirect('notifications:settings')
    
    context = {
        'settings': settings,
    }
    
    return render(request, 'notifications/settings.html', context)


@login_required
def get_unread_count(request):
    """API pour récupérer le nombre de notifications non lues"""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})