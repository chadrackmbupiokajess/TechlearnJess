from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils import timezone

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


@login_required
def get_latest_notifications(request):
    """API pour le polling AJAX des notifications"""
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    recent_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]

    notification_data = []
    for notif in recent_notifications:
        icon_class = 'fas fa-info-circle text-gray-500'
        if notif.notification_type == 'course_new':
            icon_class = 'fas fa-book text-blue-500'
        elif notif.notification_type == 'course_update':
            icon_class = 'fas fa-book-reader text-blue-500'
        elif notif.notification_type == 'lesson_new':
            icon_class = 'fas fa-file-alt text-green-500'
        elif notif.notification_type == 'message':
            icon_class = 'fas fa-comments text-purple-500'
        elif notif.notification_type == 'forum_reply':
            icon_class = 'fas fa-reply text-indigo-500'
        elif notif.notification_type == 'live_session':
            icon_class = 'fas fa-video text-red-500'
        elif notif.notification_type == 'certificate':
            icon_class = 'fas fa-certificate text-yellow-500'
        elif notif.notification_type == 'payment':
            icon_class = 'fas fa-credit-card text-orange-500'

        notification_data.append({
            'id': notif.id,
            'title': notif.title,
            'message': notif.message,
            'action_url': notif.action_url,
            'is_read': notif.is_read,
            'created_at': naturaltime(notif.created_at),
            'icon_class': icon_class,
        })

    return JsonResponse({
        'unread_count': unread_count,
        'notifications': notification_data,
    })
