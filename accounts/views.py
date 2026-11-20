from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from .forms import TeacherLoginForm, StudentLoginForm
from .models import UserProfile


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


@login_required(login_url="teacher_login")
def teacher_dashboard(request):
    """Teacher dashboard view - requires TEACHER role."""
    try:
        profile = request.user.profile
        if profile.role != UserProfile.Role.TEACHER:
            raise PermissionDenied("Only teachers can access this page.")
    except UserProfile.DoesNotExist:
        raise PermissionDenied("User profile not found.")

    return render(request, "accounts/teacher_dashboard.html", {
        "user": request.user,
        "profile": profile
    })
