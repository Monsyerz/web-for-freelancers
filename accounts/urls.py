from django.urls import path

from .views import TeacherLoginView, StudentLoginView

urlpatterns = [
    path("teacher/login/", TeacherLoginView.as_view(), name="teacher_login"),
    path("student/login/", StudentLoginView.as_view(), name="student_login"),
]
