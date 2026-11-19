from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
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
