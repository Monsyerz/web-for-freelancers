from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
from django.urls import reverse
from .models import UserProfile


class UserProfileModelTest(TestCase):
    """Tests for UserProfile model creation and role validation."""

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def test_create_profile_with_teacher_role(self):
        """Profile can be created with teacher role."""
        profile = UserProfile.objects.create(
            user=self.user,
            role=UserProfile.Role.TEACHER,
            display_name="Test Teacher"
        )
        self.assertEqual(profile.role, "teacher")
        self.assertEqual(profile.display_name, "Test Teacher")

    def test_create_profile_with_student_role(self):
        """Profile can be created with student role."""
        profile = UserProfile.objects.create(
            user=self.user,
            role=UserProfile.Role.STUDENT,
            display_name="Test Student"
        )
        self.assertEqual(profile.role, "student")

    def test_profile_linked_to_user(self):
        """Profile is linked to user via OneToOneField."""
        profile = UserProfile.objects.create(
            user=self.user,
            role=UserProfile.Role.TEACHER
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(self.user.profile, profile)

    def test_user_can_have_only_one_profile(self):
        """A user can have only one profile (OneToOne constraint)."""
        UserProfile.objects.create(
            user=self.user,
            role=UserProfile.Role.TEACHER
        )
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                UserProfile.objects.create(
                    user=self.user,
                    role=UserProfile.Role.STUDENT
                )

    def test_profile_deleted_when_user_deleted(self):
        """Profile is deleted when the user is deleted (CASCADE)."""
        profile = UserProfile.objects.create(
            user=self.user,
            role=UserProfile.Role.TEACHER
        )
        profile_id = profile.id
        self.user.delete()
        self.assertFalse(UserProfile.objects.filter(id=profile_id).exists())

    def test_role_choices_valid(self):
        """Role field accepts only valid choices."""
        valid_roles = [choice[0] for choice in UserProfile.Role.choices]
        self.assertIn("teacher", valid_roles)
        self.assertIn("student", valid_roles)

    def test_invalid_role_raises_validation_error(self):
        """Invalid role value raises ValidationError on full_clean()."""
        profile = UserProfile(
            user=self.user,
            role="invalid_role",
            display_name="Test"
        )
        with self.assertRaises(ValidationError):
            profile.full_clean()


class TeacherLoginTest(TestCase):
    """Tests for Teacher login view and form."""

    def setUp(self):
        User = get_user_model()
        self.teacher = User.objects.create_user(
            username="teacher_user",
            email="teacher@example.com",
            password="teacherpass123"
        )
        UserProfile.objects.create(
            user=self.teacher,
            role=UserProfile.Role.TEACHER,
            display_name="Test Teacher"
        )

        self.student = User.objects.create_user(
            username="student_user",
            email="student@example.com",
            password="studentpass123"
        )
        UserProfile.objects.create(
            user=self.student,
            role=UserProfile.Role.STUDENT,
            display_name="Test Student"
        )

    def test_teacher_can_login(self):
        """Teacher with valid credentials can log in and is redirected."""
        response = self.client.post(
            reverse("teacher_login"),
            {
                "username": "teacher_user",
                "password": "teacherpass123"
            }
        )
        self.assertRedirects(response, reverse("landing"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_student_cannot_login_as_teacher(self):
        """Student with valid credentials is rejected by Teacher Login."""
        response = self.client.post(
            reverse("teacher_login"),
            {
                "username": "student_user",
                "password": "studentpass123"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_user_without_profile_cannot_login(self):
        """User without a UserProfile cannot log in through Teacher Login."""
        User = get_user_model()
        user_no_profile = User.objects.create_user(
            username="no_profile_user",
            email="nop@example.com",
            password="nopass123"
        )
        response = self.client.post(
            reverse("teacher_login"),
            {
                "username": "no_profile_user",
                "password": "nopass123"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_teacher_with_wrong_password_cannot_login(self):
        """Teacher with incorrect password cannot log in."""
        response = self.client.post(
            reverse("teacher_login"),
            {
                "username": "teacher_user",
                "password": "wrongpassword"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_teacher_safe_next_redirect(self):
        """Teacher login redirects to safe next URL."""
        response = self.client.post(
            reverse("teacher_login"),
            {
                "username": "teacher_user",
                "password": "teacherpass123",
                "next": "/example/"
            }
        )
        self.assertRedirects(
            response,
            "/example/",
            fetch_redirect_response=False,
        )

    def test_teacher_external_next_redirect_rejected(self):
        """External next URL is rejected; redirect to landing instead."""
        response = self.client.post(
            reverse("teacher_login"),
            {
                "username": "teacher_user",
                "password": "teacherpass123",
                "next": "https://evil.example/"
            }
        )
        self.assertRedirects(response, reverse("landing"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_teacher_login_rejected_without_csrf_token(self):
        """Login without CSRF token is rejected with 403."""
        client = Client(enforce_csrf_checks=True)
        response = client.post(
            reverse("teacher_login"),
            {
                "username": "teacher_user",
                "password": "teacherpass123"
            }
        )
        self.assertEqual(response.status_code, 403)
        self.assertNotIn("_auth_user_id", client.session)

    def test_teacher_login_succeeds_with_valid_csrf_token(self):
        """Login with valid CSRF token succeeds."""
        client = Client(enforce_csrf_checks=True)
        client.get(reverse("teacher_login"))
        csrf_token = client.cookies["csrftoken"].value
        response = client.post(
            reverse("teacher_login"),
            {
                "username": "teacher_user",
                "password": "teacherpass123",
                "csrfmiddlewaretoken": csrf_token
            }
        )
        self.assertRedirects(response, reverse("landing"))
        self.assertIn("_auth_user_id", client.session)
