# questions/models.py
from django.db import models
from django.conf import settings

class Exam(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    topic = models.CharField(max_length=200, blank=True)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="exams")
    start_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(help_text="مدت به دقیقه")
    total_score = models.FloatField(default=100.0)
    created_at = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(default=False)

    class Meta:
        ordering = ("-start_at",)

    def __str__(self):
        return f"{self.title} ({self.topic})"

class Question(models.Model):
    TYPE_SHORT = "short"
    TYPE_MCQ = "mcq"
    TYPE_FILE = "file"
    TYPE_CHOICES = (
        (TYPE_SHORT, "پاسخ کوتاه"),
        (TYPE_MCQ, "چندگزینه‌ای"),
        (TYPE_FILE, "پاسخ حاوی فایل"),
    )

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    qtype = models.CharField(max_length=16, choices=TYPE_CHOICES)
    max_score = models.FloatField(default=1.0)
    auto_grade_regex = models.CharField(max_length=500, blank=True, null=True,
                                        help_text="در صورت تمایل، regex یا عبارت برای نمره‌دهی خودکار")
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("order",)

    def __str__(self):
        return f"Q{self.pk} ({self.qtype}) - {self.text[:40]}"

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=1000)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("order",)

    def __str__(self):
        return f"Choice {self.pk} for Q{self.question_id}"
