# grading/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

from attempts.models import Answer, Attempt

class ManualReview(models.Model):
    answer = models.OneToOneField(Answer, on_delete=models.CASCADE, related_name="manual_review")
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviews")
    comments = models.TextField(blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    final_score = models.FloatField(blank=True, null=True)

    def complete(self, reviewer, score, comments=""):
        self.reviewer = reviewer
        self.final_score = score
        self.comments = comments
        self.reviewed_at = timezone.now()
        self.save()
        # update associated answer
        ans = self.answer
        ans.score = score
        ans.graded_by = reviewer
        ans.graded_at = self.reviewed_at
        ans.is_auto_graded = False
        ans.needs_manual = False
        ans.save()

    def __str__(self):
        return f"ManualReview for Answer {self.answer_id}"

class AutoGraderLog(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name="autograde_logs")
    matched = models.BooleanField()
    awarded_score = models.FloatField(blank=True, null=True)
    reason = models.TextField(blank=True)
    run_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AutogradeLog {self.pk} for Answer {self.answer_id}"
