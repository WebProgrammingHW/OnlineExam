# notifications/models.py
from django.db import models
from django.conf import settings

class Notification(models.Model):
    TYPE_CHOICES = (
        ("score", "اعلام نمره"),
        ("system", "سیستم"),
        ("reminder", "یادآوری"),
    )
    CHANNEL_CHOICES = (
        ("email", "ایمیل"),
        ("sms", "پیامک"),
        ("in_app", "درون‌برنامه‌ای"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    notif_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default="system")
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default="in_app")
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(blank=True, null=True)
    extra = models.JSONField(blank=True, null=True)

    def mark_sent(self):
        self.sent = True
        from django.utils import timezone
        self.sent_at = timezone.now()
        self.save()

    def __str__(self):
        return f"Notification to {self.user} - {self.title}"
