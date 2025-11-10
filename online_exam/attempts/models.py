# attempts/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

from questions.models import Exam, Question, Choice

class Attempt(models.Model):
    STATUS_CHOICES = (
        ("in_progress", "در حال انجام"),
        ("submitted", "ارسال شده"),
        ("graded", "نمره‌گذاری شده"),
        ("cancelled", "لغو شده"),
    )

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attempts")
    exam = models.ForeignKey(Exam, on_delete=models.PROTECT, related_name="attempts")
    start_time = models.DateTimeField(default=timezone.now)
    submitted_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="in_progress")
    total_score = models.FloatField(blank=True, null=True)

    class Meta:
        unique_together = ("student", "exam")
        ordering = ("-start_time",)

    def submit(self):
        self.submitted_at = timezone.now()
        self.status = "submitted"
        self.save()

    def __str__(self):
        return f"Attempt: {self.student} - {self.exam}"

class Answer(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    text_answer = models.TextField(blank=True, null=True)
    selected_choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, blank=True, null=True)
    uploaded_file = models.FileField(upload_to="answers/files/", blank=True, null=True)
    score = models.FloatField(blank=True, null=True)
    graded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="graded_answers")
    graded_at = models.DateTimeField(blank=True, null=True)
    is_auto_graded = models.BooleanField(default=False)
    needs_manual = models.BooleanField(default=False)

    class Meta:
        unique_together = ("attempt", "question")

    def mark_needs_manual(self):
        self.needs_manual = True
        self.save()

    def __str__(self):
        return f"Answer Q{self.question_id} by {self.attempt.student}"
