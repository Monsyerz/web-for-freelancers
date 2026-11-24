from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
from django.urls import resolve, reverse
from django.core.management import call_command
from django.core.management.base import CommandError
from io import StringIO
import os
import unittest.mock

from .models import UserProfile
from lessons.models import Lesson, TeacherStudent
from django.utils import timezone


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
        self.assertRedirects(response, reverse("teacher_dashboard"))
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
        """External next URL is rejected; redirect to the teacher dashboard instead."""
        response = self.client.post(
            reverse("teacher_login"),
            {
                "username": "teacher_user",
                "password": "teacherpass123",
                "next": "https://evil.example/"
            }
        )
        self.assertRedirects(response, reverse("teacher_dashboard"))
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
        self.assertRedirects(response, reverse("teacher_dashboard"))
        self.assertIn("_auth_user_id", client.session)


class StudentLoginTest(TestCase):
    """Tests for Student login view and form."""

    def setUp(self):
        User = get_user_model()
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

    def test_student_login_page_renders(self):
        """GET student_login returns 200 and uses student template."""
        response = self.client.get(reverse("student_login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/student_login.html")

    def test_student_can_login(self):
        """Student with valid credentials can log in and is redirected."""
        response = self.client.post(
            reverse("student_login"),
            {
                "username": "student_user",
                "password": "studentpass123"
            }
        )
        self.assertRedirects(response, reverse("landing"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_teacher_cannot_login_as_student(self):
        """Teacher with valid credentials is rejected by Student Login."""
        response = self.client.post(
            reverse("student_login"),
            {
                "username": "teacher_user",
                "password": "teacherpass123"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_student_with_wrong_password_cannot_login(self):
        """Student with incorrect password cannot log in."""
        response = self.client.post(
            reverse("student_login"),
            {
                "username": "student_user",
                "password": "wrongpassword"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_student_login_rejected_without_csrf_token(self):
        """Login without CSRF token is rejected with 403."""
        client = Client(enforce_csrf_checks=True)
        response = client.post(
            reverse("student_login"),
            {
                "username": "student_user",
                "password": "studentpass123"
            }
        )
        self.assertEqual(response.status_code, 403)
        self.assertNotIn("_auth_user_id", client.session)

    def test_student_login_succeeds_with_valid_csrf_token(self):
        """Login with valid CSRF token succeeds."""
        client = Client(enforce_csrf_checks=True)
        client.get(reverse("student_login"))
        csrf_token = client.cookies["csrftoken"].value
        response = client.post(
            reverse("student_login"),
            {
                "username": "student_user",
                "password": "studentpass123",
                "csrfmiddlewaretoken": csrf_token
            }
        )
        self.assertRedirects(response, reverse("landing"))
        self.assertIn("_auth_user_id", client.session)

    def test_student_external_next_redirect_rejected(self):
        """External next URL is rejected; redirect to landing instead."""
        response = self.client.post(
            reverse("student_login"),
            {
                "username": "student_user",
                "password": "studentpass123",
                "next": "https://evil.example.com"
            }
        )
        self.assertRedirects(response, reverse("landing"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_user_without_profile_cannot_login_as_student(self):
        """User without a UserProfile cannot log in through Student Login."""
        User = get_user_model()
        user_no_profile = User.objects.create_user(
            username="no_profile_user",
            email="nop@example.com",
            password="nopass123"
        )
        response = self.client.post(
            reverse("student_login"),
            {
                "username": "no_profile_user",
                "password": "nopass123"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class LogoutTest(TestCase):
    """Tests for secure POST-only logout."""

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

    def test_teacher_can_logout(self):
        """Authenticated Teacher can log out via POST."""
        self.client.login(username="teacher_user", password="teacherpass123")
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("landing"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_student_can_logout(self):
        """Authenticated Student can log out via POST."""
        self.client.login(username="student_user", password="studentpass123")
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("landing"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_redirects_to_landing(self):
        """Successful logout redirects to the landing page."""
        self.client.login(username="teacher_user", password="teacherpass123")
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("landing"))

    def test_logout_removes_session(self):
        """After logout, the authenticated session is removed."""
        self.client.login(username="teacher_user", password="teacherpass123")
        self.assertIn("_auth_user_id", self.client.session)
        self.client.post(reverse("logout"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_get_logout_returns_405(self):
        """GET /accounts/logout/ returns HTTP 405."""
        self.client.login(username="teacher_user", password="teacherpass123")
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)

    def test_get_logout_does_not_log_out(self):
        """GET /accounts/logout/ does not log out an authenticated user."""
        self.client.login(username="teacher_user", password="teacherpass123")
        self.client.get(reverse("logout"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_logout_without_csrf_token_returns_403(self):
        """POST without CSRF token returns 403 when CSRF enforcement is enabled."""
        client = Client(enforce_csrf_checks=True)
        client.login(username="teacher_user", password="teacherpass123")
        response = client.post(reverse("logout"))
        self.assertEqual(response.status_code, 403)
        self.assertIn("_auth_user_id", client.session)

    def test_logout_with_valid_csrf_token_succeeds(self):
        """POST with valid CSRF token successfully logs out the user."""
        client = Client(enforce_csrf_checks=True)
        client.login(username="teacher_user", password="teacherpass123")
        client.get(reverse("teacher_login"))
        csrf_token = client.cookies["csrftoken"].value
        response = client.post(
            reverse("logout"),
            {"csrfmiddlewaretoken": csrf_token}
        )
        self.assertRedirects(response, reverse("landing"))
        self.assertNotIn("_auth_user_id", client.session)


class TeacherDashboardTest(TestCase):
    """Tests for Teacher Dashboard access control."""

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

    def test_teacher_can_access_dashboard(self):
        """Authenticated teacher can access the dashboard."""
        self.client.login(username="teacher_user", password="teacherpass123")
        response = self.client.get(reverse("teacher_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/teacher_dashboard.html")

    def test_anonymous_user_cannot_access_dashboard(self):
        """Anonymous user is redirected to login when accessing dashboard."""
        response = self.client.get(reverse("teacher_dashboard"))
        self.assertRedirects(response, f"{reverse('teacher_login')}?next={reverse('teacher_dashboard')}")

    def test_student_cannot_access_teacher_dashboard(self):
        """Student is denied access to teacher dashboard with HTTP 403."""
        self.client.login(username="student_user", password="studentpass123")
        response = self.client.get(reverse("teacher_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_user_without_profile_cannot_access_dashboard(self):
        """User without profile is denied access to teacher dashboard with HTTP 403."""
        User = get_user_model()
        user_no_profile = User.objects.create_user(
            username="no_profile_user",
            email="nop@example.com",
            password="nopass123"
        )
        self.client.login(username="no_profile_user", password="nopass123")
        response = self.client.get(reverse("teacher_dashboard"))
        self.assertEqual(response.status_code, 403)

    placeholder_pages = (
        ("teacher_lessons", "Lessons"),
        ("teacher_students", "Students"),
        ("teacher_homework", "Homework"),
        ("teacher_notes", "Notes"),
    )

    def test_placeholder_routes(self):
        for name, title in self.placeholder_pages:
            with self.subTest(page=name):
                url = f"/accounts/teacher/{title.lower()}/"
                self.assertEqual(reverse(name), url)
                self.assertEqual(resolve(url).url_name, name)

    def test_teacher_can_access_placeholder_pages(self):
        self.client.force_login(self.teacher)
        for name, title in self.placeholder_pages:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertTemplateUsed(response, f"accounts/{name}.html")
                self.assertContains(response, f"<h1>{title}</h1>", html=True)
                self.assertContains(response, "Under Construction")

    def test_anonymous_user_redirected_from_placeholder_pages(self):
        login_url = reverse("teacher_login")
        for name, _ in self.placeholder_pages:
            with self.subTest(page=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertRedirects(response, f"{login_url}?next={url}")

    def test_student_cannot_access_placeholder_pages(self):
        self.client.force_login(self.student)
        for name, _ in self.placeholder_pages:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 403)

    def test_user_without_profile_cannot_access_placeholder_pages(self):
        user = get_user_model().objects.create_user(username="no_profile")
        self.client.force_login(user)
        for name, _ in self.placeholder_pages:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 403)

    def test_teacher_sidebar_navigation(self):
        self.client.force_login(self.teacher)
        sidebar_pages = (("teacher_dashboard", "Dashboard"), *self.placeholder_pages)
        for current_name, _ in sidebar_pages:
            with self.subTest(page=current_name):
                response = self.client.get(reverse(current_name))
                for name, title in sidebar_pages:
                    url = reverse(name)
                    attributes = 'class="sidebar-link"'
                    if name == current_name:
                        attributes = 'class="sidebar-link active" aria-current="page"'
                    self.assertContains(
                        response, f'<a href="{url}" {attributes}>{title}</a>', html=True
                    )


class SeedDemoAccountsTest(TestCase):
    """Tests for the seed_demo_accounts management command."""

    def setUp(self):
        # Clear demo password env vars to ensure isolation
        self.env_patcher = unittest.mock.patch.dict(
            os.environ,
            {"DEMO_TEACHER_PASSWORD": "", "DEMO_STUDENT_PASSWORD": ""},
            clear=False
        )
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    def _set_env(self, teacher_password, student_password):
        """Set environment variables for demo passwords."""
        env = {}
        if teacher_password is not None:
            env["DEMO_TEACHER_PASSWORD"] = teacher_password
        if student_password is not None:
            env["DEMO_STUDENT_PASSWORD"] = student_password
        self.env_patcher = unittest.mock.patch.dict(os.environ, env, clear=False)
        self.env_patcher.start()

    def test_creates_teacher_and_student_accounts(self):
        """Command creates both teacher and student demo accounts."""
        self._set_env("teacher_pass_123", "student_pass_123")

        out = StringIO()
        call_command("seed_demo_accounts", stdout=out)

        User = get_user_model()
        teacher = User.objects.get(username="demo_teacher")
        student = User.objects.get(username="demo_student")

        self.assertEqual(teacher.profile.role, UserProfile.Role.TEACHER)
        self.assertEqual(student.profile.role, UserProfile.Role.STUDENT)
        self.assertTrue(teacher.check_password("teacher_pass_123"))
        self.assertTrue(student.check_password("student_pass_123"))

    def test_accounts_can_login(self):
        """Created demo accounts can authenticate through login forms."""
        self._set_env("teacher_pass_123", "student_pass_123")
        call_command("seed_demo_accounts")

        # Teacher login
        response = self.client.post(
            reverse("teacher_login"),
            {"username": "demo_teacher", "password": "teacher_pass_123"}
        )
        self.assertRedirects(response, reverse("teacher_dashboard"))

        self.client.logout()

        # Student login
        response = self.client.post(
            reverse("student_login"),
            {"username": "demo_student", "password": "student_pass_123"}
        )
        self.assertRedirects(response, reverse("landing"))

    def test_idempotent_repeated_execution(self):
        """Running the command twice does not create duplicate accounts."""
        self._set_env("teacher_pass_123", "student_pass_123")

        call_command("seed_demo_accounts")
        call_command("seed_demo_accounts")

        User = get_user_model()
        self.assertEqual(User.objects.filter(username="demo_teacher").count(), 1)
        self.assertEqual(User.objects.filter(username="demo_student").count(), 1)

    def test_does_not_reset_existing_passwords(self):
        """Existing accounts keep their original passwords."""
        User = get_user_model()
        existing_teacher = User.objects.create_user(
            username="demo_teacher",
            password="original_password",
            email="demo_teacher@demo.local"
        )
        UserProfile.objects.create(
            user=existing_teacher,
            role=UserProfile.Role.TEACHER,
            display_name="Demo Teacher"
        )

        self._set_env("new_password", "student_pass_123")
        call_command("seed_demo_accounts")

        self.assertTrue(existing_teacher.check_password("original_password"))

    def test_fails_when_teacher_password_missing(self):
        """Command fails if DEMO_TEACHER_PASSWORD is not set."""
        self._set_env(None, "student_pass_123")

        with self.assertRaises(CommandError) as ctx:
            call_command("seed_demo_accounts")
        self.assertIn("DEMO_TEACHER_PASSWORD", str(ctx.exception))

    def test_fails_when_student_password_missing(self):
        """Command fails if DEMO_STUDENT_PASSWORD is not set."""
        self._set_env("teacher_pass_123", None)

        with self.assertRaises(CommandError) as ctx:
            call_command("seed_demo_accounts")
        self.assertIn("DEMO_STUDENT_PASSWORD", str(ctx.exception))

    def test_fails_on_username_collision_wrong_role(self):
        """Command fails if username exists with wrong role."""
        User = get_user_model()
        wrong_role_user = User.objects.create_user(
            username="demo_teacher",
            password="somepass",
            email="demo_teacher@demo.local"
        )
        UserProfile.objects.create(
            user=wrong_role_user,
            role=UserProfile.Role.STUDENT,
            display_name="Demo Teacher"
        )

        self._set_env("teacher_pass_123", "student_pass_123")

        with self.assertRaises(CommandError) as ctx:
            call_command("seed_demo_accounts")
        self.assertIn("role", str(ctx.exception).lower())

    def test_custom_usernames(self):
        """Command supports custom usernames via arguments."""
        self._set_env("teacher_pass_123", "student_pass_123")

        call_command(
            "seed_demo_accounts",
            "--teacher-username", "custom_teacher",
            "--student-username", "custom_student"
        )

        User = get_user_model()
        self.assertTrue(User.objects.filter(username="custom_teacher").exists())
        self.assertTrue(User.objects.filter(username="custom_student").exists())

    def test_partial_failure_rolls_back_all_changes(self):
        """If student creation fails, teacher creation is rolled back."""
        User = get_user_model()

        # Pre-create student with wrong role to trigger failure
        wrong_role_student = User.objects.create_user(
            username="demo_student",
            password="somepass",
            email="demo_student@demo.local"
        )
        UserProfile.objects.create(
            user=wrong_role_student,
            role=UserProfile.Role.TEACHER,
            display_name="Demo Student"
        )

        self._set_env("teacher_pass_123", "student_pass_123")

        with self.assertRaises(CommandError):
            call_command("seed_demo_accounts")

        # Teacher should not have been created (rolled back)
        self.assertFalse(User.objects.filter(username="demo_teacher").exists())

    def test_fails_on_existing_account_with_wrong_email(self):
        """Command fails if existing account has correct role but wrong email."""
        User = get_user_model()
        existing_user = User.objects.create_user(
            username="demo_teacher",
            password="somepass",
            email="wrong@example.com"
        )
        UserProfile.objects.create(
            user=existing_user,
            role=UserProfile.Role.TEACHER,
            display_name="Demo Teacher"
        )

        self._set_env("teacher_pass_123", "student_pass_123")

        with self.assertRaises(CommandError) as ctx:
            call_command("seed_demo_accounts")
        self.assertIn("email", str(ctx.exception).lower())

    def test_fails_on_existing_account_with_wrong_display_name(self):
        """Command fails if existing account has correct role but wrong display name."""
        User = get_user_model()
        existing_user = User.objects.create_user(
            username="demo_teacher",
            password="somepass",
            email="demo_teacher@demo.local"
        )
        UserProfile.objects.create(
            user=existing_user,
            role=UserProfile.Role.TEACHER,
            display_name="Wrong Name"
        )

        self._set_env("teacher_pass_123", "student_pass_123")

        with self.assertRaises(CommandError) as ctx:
            call_command("seed_demo_accounts")
        self.assertIn("display name", str(ctx.exception).lower())


class TeacherDashboardLessonTest(TestCase):
    """Tests for Teacher Dashboard lesson display."""

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

        self.student1 = User.objects.create_user(
            username="student1",
            email="student1@example.com",
            password="studentpass123"
        )
        UserProfile.objects.create(
            user=self.student1,
            role=UserProfile.Role.STUDENT,
            display_name="Student One"
        )

        self.student2 = User.objects.create_user(
            username="student2",
            email="student2@example.com",
            password="studentpass123"
        )
        UserProfile.objects.create(
            user=self.student2,
            role=UserProfile.Role.STUDENT,
            display_name="Student Two"
        )

        TeacherStudent.objects.create(
            teacher=self.teacher,
            student=self.student1
        )
        TeacherStudent.objects.create(
            teacher=self.teacher,
            student=self.student2
        )

    def test_upcoming_lessons_displayed(self):
        """Upcoming lessons are displayed with student name, topic, date, and duration."""
        now = timezone.now()
        future_lesson1 = Lesson.objects.create(
            teacher=self.teacher,
            student=self.student1,
            topic="Math",
            scheduled_at=now + timezone.timedelta(days=1),
            duration_minutes=60
        )
        future_lesson2 = Lesson.objects.create(
            teacher=self.teacher,
            student=self.student2,
            topic="Science",
            scheduled_at=now + timezone.timedelta(days=2),
            duration_minutes=45
        )

        self.client.login(username="teacher_user", password="teacherpass123")
        response = self.client.get(reverse("teacher_dashboard"))

        self.assertContains(response, future_lesson1.student.profile.display_name)
        self.assertContains(response, future_lesson1.topic)
        self.assertContains(response, timezone.localtime(future_lesson1.scheduled_at).strftime("%Y-%m-%d %H:%M"))
        self.assertContains(response, str(future_lesson1.duration_minutes))

        self.assertContains(response, future_lesson2.student.profile.display_name)
        self.assertContains(response, future_lesson2.topic)
        self.assertContains(response, timezone.localtime(future_lesson2.scheduled_at).strftime("%Y-%m-%d %H:%M"))
        self.assertContains(response, str(future_lesson2.duration_minutes))

    def test_upcoming_lessons_ordered_by_scheduled_at(self):
        """Upcoming lessons are ordered by scheduled_at ascending."""
        now = timezone.now()
        future_lesson1 = Lesson.objects.create(
            teacher=self.teacher,
            student=self.student1,
            topic="Math",
            scheduled_at=now + timezone.timedelta(days=2),
            duration_minutes=60
        )
        future_lesson2 = Lesson.objects.create(
            teacher=self.teacher,
            student=self.student2,
            topic="Science",
            scheduled_at=now + timezone.timedelta(days=1),
            duration_minutes=45
        )

        self.client.login(username="teacher_user", password="teacherpass123")
        response = self.client.get(reverse("teacher_dashboard"))

        lessons = response.context["upcoming_lessons"]
        self.assertEqual(list(lessons), [future_lesson2, future_lesson1])

    def test_past_lessons_excluded(self):
        """Past lessons are excluded from the dashboard."""
        now = timezone.now()
        past_lesson = Lesson.objects.create(
            teacher=self.teacher,
            student=self.student1,
            topic="History",
            scheduled_at=now - timezone.timedelta(days=1),
            duration_minutes=30
        )

        self.client.login(username="teacher_user", password="teacherpass123")
        response = self.client.get(reverse("teacher_dashboard"))

        lessons = response.context["upcoming_lessons"]
        self.assertNotIn(past_lesson, lessons)

    def test_no_upcoming_lessons_empty_state(self):
        """A teacher with no upcoming lessons sees the empty state."""
        self.client.login(username="teacher_user", password="teacherpass123")
        response = self.client.get(reverse("teacher_dashboard"))

        lessons = response.context["upcoming_lessons"]
        self.assertFalse(lessons.exists())
        self.assertContains(response, "No upcoming lessons scheduled.")

    def test_teacher_cannot_see_other_teacher_lessons(self):
        """A teacher cannot see another teacher's lessons."""
        other_teacher = get_user_model().objects.create_user(
            username="other_teacher",
            email="other_teacher@example.com",
            password="otherpass123"
        )
        UserProfile.objects.create(
            user=other_teacher,
            role=UserProfile.Role.TEACHER,
            display_name="Other Teacher"
        )

        other_student = get_user_model().objects.create_user(
            username="other_student",
            email="other_student@example.com",
            password="otherpass123"
        )
        UserProfile.objects.create(
            user=other_student,
            role=UserProfile.Role.STUDENT,
            display_name="Other Student"
        )

        TeacherStudent.objects.create(
            teacher=other_teacher,
            student=other_student
        )

        other_lesson = Lesson.objects.create(
            teacher=other_teacher,
            student=other_student,
            topic="Other Topic",
            scheduled_at=timezone.now() + timezone.timedelta(days=1),
            duration_minutes=60
        )

        self.client.login(username="teacher_user", password="teacherpass123")
        response = self.client.get(reverse("teacher_dashboard"))

        lessons = response.context["upcoming_lessons"]
        self.assertNotIn(other_lesson, lessons)

    def test_meeting_url_displayed(self):
        """A lesson with meeting_url displays a Join Meeting link with the correct href."""
        now = timezone.now()
        lesson_with_meeting = Lesson.objects.create(
            teacher=self.teacher,
            student=self.student1,
            topic="Math",
            scheduled_at=now + timezone.timedelta(days=1),
            duration_minutes=60,
            meeting_url="https://example.com/meeting"
        )

        self.client.login(username="teacher_user", password="teacherpass123")
        response = self.client.get(reverse("teacher_dashboard"))

        self.assertContains(response, 'href="https://example.com/meeting"')
        self.assertContains(response, 'target="_blank"')
        self.assertContains(response, 'rel="noopener noreferrer"')
        self.assertContains(response, 'Join Meeting')

    def test_no_meeting_url_displayed(self):
        """A lesson without meeting_url displays Not provided."""
        now = timezone.now()
        lesson_without_meeting = Lesson.objects.create(
            teacher=self.teacher,
            student=self.student1,
            topic="Math",
            scheduled_at=now + timezone.timedelta(days=1),
            duration_minutes=60,
            meeting_url=""
        )

        self.client.login(username="teacher_user", password="teacherpass123")
        response = self.client.get(reverse("teacher_dashboard"))

        self.assertContains(response, 'Not provided')
