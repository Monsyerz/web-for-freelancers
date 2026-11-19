from django.db import models
from django.conf import settings


class UserProfile(models.Model):
    """Profile linked to Django User with role information."""

    class Role(models.TextChoices):
        TEACHER = "teacher", "Teacher"
        STUDENT = "student", "Student"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    role = models.CharField(max_length=10, choices=Role.choices)
    display_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"
