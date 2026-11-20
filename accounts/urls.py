from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import TeacherLoginView, StudentLoginView, teacher_dashboard

urlpatterns = [
    path("teacher/login/", TeacherLoginView.as_view(), name="teacher_login"),
    path("student/login/", StudentLoginView.as_view(), name="student_login"),
    path("logout/", LogoutView.as_view(next_page="landing"), name="logout"),
    path("teacher/dashboard/", teacher_dashboard, name="teacher_dashboard"),
]
