from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class TeacherStudent(models.Model):
    """Relacja nauczyciel-student. Jeden nauczyciel może mieć wielu studentów,
    ale każdy student należy tylko do jednego nauczyciela."""

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="taught_students",
        limit_choices_to={"profile__role": "teacher"}
    )
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assigned_teacher",
        limit_choices_to={"profile__role": "student"}
    )

    class Meta:
        verbose_name = "Teacher-Student Relationship"
        verbose_name_plural = "Teacher-Student Relationships"

    def clean(self):
        super().clean()
        if self.teacher == self.student:
            raise ValidationError("Teacher and student must be different users.")
        if not hasattr(self.teacher, "profile") or self.teacher.profile.role != "teacher":
            raise ValidationError("Teacher must have the TEACHER role.")
        if not hasattr(self.student, "profile") or self.student.profile.role != "student":
            raise ValidationError("Student must have the STUDENT role.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.teacher.username} teaches {self.student.username}"
