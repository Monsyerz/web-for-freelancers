from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from .models import UserProfile


class TeacherLoginForm(AuthenticationForm):
    """Login form restricted to Teacher role."""

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)

        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            raise ValidationError("Nieprawidłowe dane logowania.")

        if profile.role != UserProfile.Role.TEACHER:
            raise ValidationError("Nieprawidłowe dane logowania.")
