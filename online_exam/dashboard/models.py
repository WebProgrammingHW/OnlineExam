# dashboard/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone


class DashboardPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dashboard_pref")
    prefs = models.JSONField(default=dict, blank=True) 

    def __str__(self):
        return f"DashboardPreference for {self.user}"

class ExamViewHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="exam_views")
    exam_id = models.PositiveIntegerField() 
    viewed_at = models.DateTimeField(default=timezone.now)
    action = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user} viewed exam {self.exam_id} at {self.viewed_at}"
