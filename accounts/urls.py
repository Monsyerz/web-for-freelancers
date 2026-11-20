from django.urls import path

from .views import TeacherLoginView

urlpatterns = [
    path("teacher/login/", TeacherLoginView.as_view(), name="teacher_login"),
]
