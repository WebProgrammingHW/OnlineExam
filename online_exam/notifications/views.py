# notifications/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings

from .models import Notification


@method_decorator(login_required, name='dispatch')
class NotificationListView(View):
    template_name = 'notifications/notification_list.html'

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        return render(request, self.template_name, {'notifications': notifications})


@method_decorator(login_required, name='dispatch')
class MarkAsReadView(View):
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.mark_sent()
        return redirect('notifications:list')


def send_score_notification(attempt):
    """Send score notification via email/SMS"""
    user = attempt.student
    exam = attempt.exam
    score = attempt.total_score
    
    # Create in-app notification
    Notification.objects.create(
        user=user,
        notif_type='score',
        channel='in_app',
        title=f'نمره آزمون {exam.title}',
        message=f'نمره شما: {score} از {exam.total_score}',
        extra={'exam_id': exam.id, 'attempt_id': attempt.id, 'score': score}
    )
    
    # Send email if user has email
    if user.email:
        try:
            send_mail(
                subject=f'نمره آزمون {exam.title}',
                message=f'سلام {user.get_full_name() or user.username}،\n\n'
                        f'نمره شما در آزمون {exam.title}: {score} از {exam.total_score}\n\n'
                        f'با تشکر',
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@example.com',
                recipient_list=[user.email],
                fail_silently=True
            )
            
            Notification.objects.create(
                user=user,
                notif_type='score',
                channel='email',
                title=f'نمره آزمون {exam.title}',
                message=f'ایمیل ارسال شد به {user.email}',
                sent=True
            )
        except Exception as e:
            pass
    
    # SMS would be sent here if configured
    if user.phone_number:
        # Placeholder for SMS sending
        Notification.objects.create(
            user=user,
            notif_type='score',
            channel='sms',
            title=f'نمره آزمون {exam.title}',
            message=f'پیامک به {user.phone_number}',
            extra={'phone': user.phone_number}
        )


@login_required
def unread_count(request):
    """AJAX endpoint for unread notifications count"""
    count = Notification.objects.filter(user=request.user, sent=False).count()
    return JsonResponse({'count': count})