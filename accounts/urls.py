from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import (
    StudentLoginView,
    TeacherLoginView,
    student_dashboard,
    teacher_dashboard,
    teacher_placeholder,
)

urlpatterns = [
    path("teacher/login/", TeacherLoginView.as_view(), name="teacher_login"),
    path("student/login/", StudentLoginView.as_view(), name="student_login"),
    path("student/dashboard/", student_dashboard, name="student_dashboard"),
    path("logout/", LogoutView.as_view(next_page="landing"), name="logout"),
    path("teacher/dashboard/", teacher_dashboard, name="teacher_dashboard"),
    path(
        "teacher/lessons/",
        teacher_placeholder,
        {"template_name": "accounts/teacher_lessons.html"},
        name="teacher_lessons",
    ),
    path(
        "teacher/students/",
        teacher_placeholder,
        {"template_name": "accounts/teacher_students.html"},
        name="teacher_students",
    ),
    path(
        "teacher/homework/",
        teacher_placeholder,
        {"template_name": "accounts/teacher_homework.html"},
        name="teacher_homework",
    ),
    path(
        "teacher/notes/",
        teacher_placeholder,
        {"template_name": "accounts/teacher_notes.html"},
        name="teacher_notes",
    ),
]
