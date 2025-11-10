# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ("student", "دانشجو"),
        ("teacher", "استاد"),
        ("admin", "ادمین"),
    )
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default="student")
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def is_student(self):
        return self.role == "student"

    def is_teacher(self):
        return self.role == "teacher"

    def __str__(self):
        return f"{self.username} ({self.get_full_name() or self.username})"
