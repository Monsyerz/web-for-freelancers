from django.contrib.auth.views import LoginView

from .forms import TeacherLoginForm, StudentLoginForm


class TeacherLoginView(LoginView):
    """Login view for Teacher role."""

    form_class = TeacherLoginForm
    template_name = "accounts/teacher_login.html"
    redirect_authenticated_user = False
    next_page = "landing"


class StudentLoginView(LoginView):
    """Login view for Student role."""

    form_class = StudentLoginForm
    template_name = "accounts/student_login.html"
    redirect_authenticated_user = False
    next_page = "landing"
