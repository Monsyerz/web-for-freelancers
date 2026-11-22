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


class Lesson(models.Model):
    """Zaplanowana lekcja między nauczycielem a przypisanym studentem."""

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="taught_lessons",
        limit_choices_to={"profile__role": "teacher"}
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_lessons",
        limit_choices_to={"profile__role": "student"}
    )
    topic = models.CharField(max_length=200)
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField()
    meeting_url = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = "Lesson"
        verbose_name_plural = "Lessons"
        ordering = ["scheduled_at"]

    def clean(self):
        super().clean()
        if not self.topic or not self.topic.strip():
            raise ValidationError("Topic cannot be empty.")
        if self.duration_minutes <= 0:
            raise ValidationError("Duration must be greater than zero.")
        if not hasattr(self.teacher, "profile") or self.teacher.profile.role != "teacher":
            raise ValidationError("Teacher must have the TEACHER role.")
        if not hasattr(self.student, "profile") or self.student.profile.role != "student":
            raise ValidationError("Student must have the STUDENT role.")
        try:
            TeacherStudent.objects.get(teacher=self.teacher, student=self.student)
        except TeacherStudent.DoesNotExist:
            raise ValidationError("Student must be assigned to this teacher.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.topic} - {self.student.username} ({self.scheduled_at})"
