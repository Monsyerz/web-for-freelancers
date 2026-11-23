import os

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction

from accounts.models import UserProfile

User = get_user_model()


class Command(BaseCommand):
    help = "Create fictional Teacher and Student demo accounts for local development."

    def add_arguments(self, parser):
        parser.add_argument(
            "--teacher-username",
            type=str,
            default="demo_teacher",
            help="Username for the demo teacher account (default: demo_teacher)."
        )
        parser.add_argument(
            "--student-username",
            type=str,
            default="demo_student",
            help="Username for the demo student account (default: demo_student)."
        )

    def handle(self, *args, **options):
        teacher_username = options["teacher_username"]
        student_username = options["student_username"]

        teacher_password = os.environ.get("DEMO_TEACHER_PASSWORD")
        student_password = os.environ.get("DEMO_STUDENT_PASSWORD")

        if not teacher_password:
            raise CommandError("DEMO_TEACHER_PASSWORD environment variable is not set.")
        if not student_password:
            raise CommandError("DEMO_STUDENT_PASSWORD environment variable is not set.")

        with transaction.atomic():
            self._create_or_verify_user(
                username=teacher_username,
                password=teacher_password,
                role=UserProfile.Role.TEACHER,
                display_name="Demo Teacher",
                role_label="teacher"
            )
            self.stdout.write(self.style.SUCCESS(f"Teacher account ready: {teacher_username}"))

            self._create_or_verify_user(
                username=student_username,
                password=student_password,
                role=UserProfile.Role.STUDENT,
                display_name="Demo Student",
                role_label="student"
            )
            self.stdout.write(self.style.SUCCESS(f"Student account ready: {student_username}"))

    def _create_or_verify_user(self, username, password, role, display_name, role_label):
        """Create a demo user or verify an existing one matches expectations."""
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=f"{username}@demo.local"
            )
            UserProfile.objects.create(
                user=user,
                role=role,
                display_name=display_name
            )
            self.stdout.write(self.style.SUCCESS(f"Created {role_label} account: {username}"))
            return

        # User exists - verify role, email, and display name match demo expectations
        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            raise CommandError(
                f"Username '{username}' exists but has no profile."
            )

        if profile.role != role:
            raise CommandError(
                f"Username '{username}' exists but has role '{profile.role}', "
                f"expected '{role}'."
            )

        expected_email = f"{username}@demo.local"
        if user.email != expected_email:
            raise CommandError(
                f"Username '{username}' exists but has email '{user.email}', "
                f"expected '{expected_email}'."
            )

        if profile.display_name != display_name:
            raise CommandError(
                f"Username '{username}' exists but has display name "
                f"'{profile.display_name}', expected '{display_name}'."
            )

        self.stdout.write(self.style.WARNING(f"Account already exists: {username}"))
