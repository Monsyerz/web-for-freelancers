from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta
from accounts.models import UserProfile
from lessons.models import TeacherStudent, Lesson

User = get_user_model()


class TeacherStudentModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username="teacher1", password="pass")
        UserProfile.objects.create(user=self.teacher, role="teacher", display_name="Teacher One")

        self.teacher2 = User.objects.create_user(username="teacher2", password="pass")
        UserProfile.objects.create(user=self.teacher2, role="teacher", display_name="Teacher Two")

        self.student1 = User.objects.create_user(username="student1", password="pass")
        UserProfile.objects.create(user=self.student1, role="student", display_name="Student One")

        self.student2 = User.objects.create_user(username="student2", password="pass")
        UserProfile.objects.create(user=self.student2, role="student", display_name="Student Two")

    def test_valid_relationship(self):
        ts = TeacherStudent.objects.create(teacher=self.teacher, student=self.student1)
        self.assertEqual(ts.teacher, self.teacher)
        self.assertEqual(ts.student, self.student1)

    def test_teacher_can_have_multiple_students(self):
        TeacherStudent.objects.create(teacher=self.teacher, student=self.student1)
        TeacherStudent.objects.create(teacher=self.teacher, student=self.student2)
        self.assertEqual(self.teacher.taught_students.count(), 2)

    def test_student_belongs_to_one_teacher(self):
        TeacherStudent.objects.create(teacher=self.teacher, student=self.student1)
        with self.assertRaises(IntegrityError):
            TeacherStudent.objects.create(teacher=self.teacher2, student=self.student1)

    def test_same_user_teacher_and_student_fails(self):
        with self.assertRaises(ValidationError):
            TeacherStudent.objects.create(teacher=self.teacher, student=self.teacher)

    def test_wrong_teacher_role_fails(self):
        with self.assertRaises(ValidationError):
            TeacherStudent.objects.create(teacher=self.student1, student=self.student2)

    def test_wrong_student_role_fails(self):
        with self.assertRaises(ValidationError):
            TeacherStudent.objects.create(teacher=self.teacher, student=self.teacher2)

    def test_create_rejects_invalid_teacher_role(self):
        with self.assertRaises(ValidationError):
            TeacherStudent.objects.create(teacher=self.student1, student=self.student2)

    def test_create_rejects_invalid_student_role(self):
        with self.assertRaises(ValidationError):
            TeacherStudent.objects.create(teacher=self.teacher, student=self.teacher2)


class LessonModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username="teacher1", password="pass")
        UserProfile.objects.create(user=self.teacher, role="teacher", display_name="Teacher One")

        self.teacher2 = User.objects.create_user(username="teacher2", password="pass")
        UserProfile.objects.create(user=self.teacher2, role="teacher", display_name="Teacher Two")

        self.student1 = User.objects.create_user(username="student1", password="pass")
        UserProfile.objects.create(user=self.student1, role="student", display_name="Student One")

        self.student2 = User.objects.create_user(username="student2", password="pass")
        UserProfile.objects.create(user=self.student2, role="student", display_name="Student Two")

        TeacherStudent.objects.create(teacher=self.teacher, student=self.student1)

        self.future_time = timezone.now() + timedelta(hours=2)

    def test_valid_lesson_creation(self):
        lesson = Lesson.objects.create(
            teacher=self.teacher,
            student=self.student1,
            topic="Grammar Practice",
            scheduled_at=self.future_time,
            duration_minutes=60
        )
        self.assertEqual(lesson.teacher, self.teacher)
        self.assertEqual(lesson.student, self.student1)
        self.assertEqual(lesson.topic, "Grammar Practice")
        self.assertEqual(lesson.duration_minutes, 60)

    def test_lesson_with_unassigned_student_rejected(self):
        with self.assertRaises(ValidationError):
            Lesson.objects.create(
                teacher=self.teacher,
                student=self.student2,
                topic="Test",
                scheduled_at=self.future_time,
                duration_minutes=60
            )

    def test_student_assigned_to_another_teacher_rejected(self):
        with self.assertRaises(ValidationError):
            Lesson.objects.create(
                teacher=self.teacher2,
                student=self.student1,
                topic="Test",
                scheduled_at=self.future_time,
                duration_minutes=60
            )

    def test_invalid_teacher_role_rejected(self):
        with self.assertRaises(ValidationError):
            Lesson.objects.create(
                teacher=self.student1,
                student=self.student2,
                topic="Test",
                scheduled_at=self.future_time,
                duration_minutes=60
            )

    def test_invalid_student_role_rejected(self):
        with self.assertRaises(ValidationError):
            Lesson.objects.create(
                teacher=self.teacher,
                student=self.teacher2,
                topic="Test",
                scheduled_at=self.future_time,
                duration_minutes=60
            )

    def test_zero_duration_rejected(self):
        with self.assertRaises(ValidationError):
            Lesson.objects.create(
                teacher=self.teacher,
                student=self.student1,
                topic="Test",
                scheduled_at=self.future_time,
                duration_minutes=0
            )

    def test_negative_duration_rejected(self):
        with self.assertRaises(ValidationError):
            Lesson.objects.create(
                teacher=self.teacher,
                student=self.student1,
                topic="Test",
                scheduled_at=self.future_time,
                duration_minutes=-30
            )

    def test_empty_topic_rejected(self):
        with self.assertRaises(ValidationError):
            Lesson.objects.create(
                teacher=self.teacher,
                student=self.student1,
                topic="",
                scheduled_at=self.future_time,
                duration_minutes=60
            )

    def test_whitespace_only_topic_rejected(self):
        with self.assertRaises(ValidationError):
            Lesson.objects.create(
                teacher=self.teacher,
                student=self.student1,
                topic="   ",
                scheduled_at=self.future_time,
                duration_minutes=60
            )

    def test_missing_required_lesson_fields_raise_validation_errors(self):
        fields = {
            "teacher": self.teacher,
            "student": self.student1,
            "topic": "Grammar Practice",
            "scheduled_at": self.future_time,
            "duration_minutes": 60,
        }
        for field in ("teacher", "student", "scheduled_at", "duration_minutes"):
            for method in ("full_clean", "save"):
                with self.subTest(field=field, method=method):
                    lesson = Lesson(**{**fields, field: None})
                    with self.assertRaises(ValidationError) as error:
                        getattr(lesson, method)()
                    self.assertIn(field, error.exception.message_dict)
        self.assertFalse(Lesson.objects.exists())

    def test_optional_meeting_url_accepted(self):
        lesson = Lesson.objects.create(
            teacher=self.teacher,
            student=self.student1,
            topic="Test",
            scheduled_at=self.future_time,
            duration_minutes=60
        )
        self.assertIsNone(lesson.meeting_url)

    def test_valid_meeting_url_stored(self):
        lesson = Lesson.objects.create(
            teacher=self.teacher,
            student=self.student1,
            topic="Test",
            scheduled_at=self.future_time,
            duration_minutes=60,
            meeting_url="https://teams.microsoft.com/meet/12345"
        )
        self.assertEqual(lesson.meeting_url, "https://teams.microsoft.com/meet/12345")


class SeedDemoLessonsCommandTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username="demo_teacher", password="pass")
        UserProfile.objects.create(user=self.teacher, role="teacher", display_name="Demo Teacher")

    def test_creates_demo_students(self):
        from django.core.management import call_command
        call_command("seed_demo_lessons", "demo_teacher")

        self.assertEqual(User.objects.filter(username="demo_student_anna").count(), 1)
        self.assertEqual(User.objects.filter(username="demo_student_bartek").count(), 1)
        self.assertEqual(User.objects.filter(username="demo_student_carol").count(), 1)

    def test_students_have_student_role(self):
        from django.core.management import call_command
        call_command("seed_demo_lessons", "demo_teacher")

        student = User.objects.get(username="demo_student_anna")
        self.assertEqual(student.profile.role, "student")

    def test_students_assigned_to_teacher(self):
        from django.core.management import call_command
        call_command("seed_demo_lessons", "demo_teacher")

        student = User.objects.get(username="demo_student_anna")
        self.assertEqual(student.assigned_teacher.teacher, self.teacher)

    def test_creates_five_lessons(self):
        from django.core.management import call_command
        call_command("seed_demo_lessons", "demo_teacher")

        self.assertEqual(Lesson.objects.filter(teacher=self.teacher).count(), 5)

    def test_lessons_have_future_dates(self):
        from django.core.management import call_command
        call_command("seed_demo_lessons", "demo_teacher")

        lessons = Lesson.objects.filter(teacher=self.teacher)
        for lesson in lessons:
            self.assertGreater(lesson.scheduled_at, timezone.now() - timedelta(hours=1))

    def test_idempotent_no_duplicates(self):
        from django.core.management import call_command
        call_command("seed_demo_lessons", "demo_teacher")
        call_command("seed_demo_lessons", "demo_teacher")

        self.assertEqual(User.objects.filter(username="demo_student_anna").count(), 1)
        self.assertEqual(Lesson.objects.filter(teacher=self.teacher).count(), 5)

    def test_invalid_teacher_rejected(self):
        from django.core.management import call_command
        from django.core.management.base import CommandError

        with self.assertRaisesRegex(CommandError, "does not exist"):
            call_command("seed_demo_lessons", "nonexistent_teacher")

        self.assertEqual(User.objects.filter(username="demo_student_anna").count(), 0)
        self.assertEqual(Lesson.objects.filter(teacher=self.teacher).count(), 0)

    def test_student_role_user_rejected(self):
        student = User.objects.create_user(username="just_student", password="pass")
        UserProfile.objects.create(user=student, role="student", display_name="Just Student")

        from django.core.management import call_command
        from django.core.management.base import CommandError

        with self.assertRaisesRegex(CommandError, "TEACHER"):
            call_command("seed_demo_lessons", "just_student")

        self.assertEqual(User.objects.filter(username="demo_student_anna").count(), 0)
        self.assertEqual(Lesson.objects.filter(teacher=self.teacher).count(), 0)

    def test_preserves_existing_records(self):
        existing_student = User.objects.create_user(username="existing_student", password="pass")
        UserProfile.objects.create(user=existing_student, role="student", display_name="Existing")
        TeacherStudent.objects.create(teacher=self.teacher, student=existing_student)

        from django.core.management import call_command
        call_command("seed_demo_lessons", "demo_teacher")

        self.assertEqual(User.objects.filter(username="existing_student").count(), 1)
        self.assertEqual(TeacherStudent.objects.filter(teacher=self.teacher).count(), 4)

    def test_conflicting_username_not_student_role(self):
        """Test that existing username with non-student role raises error."""
        from django.core.management import call_command
        from django.core.management.base import CommandError

        # Create user with demo username but teacher role
        conflicting_user = User.objects.create_user(username="demo_student_anna", password="pass")
        UserProfile.objects.create(user=conflicting_user, role="teacher", display_name="Conflicting")

        with self.assertRaisesRegex(CommandError, "not a student"):
            call_command("seed_demo_lessons", "demo_teacher")

        # Verify no changes were made
        self.assertEqual(Lesson.objects.filter(teacher=self.teacher).count(), 0)
        self.assertEqual(TeacherStudent.objects.filter(teacher=self.teacher).count(), 0)

    def test_conflicting_username_not_assigned_to_teacher(self):
        """Test that existing username not assigned to teacher raises error."""
        from django.core.management import call_command
        from django.core.management.base import CommandError

        # Create user with demo username, student role, but assigned to different teacher
        other_teacher = User.objects.create_user(username="other_teacher", password="pass")
        UserProfile.objects.create(user=other_teacher, role="teacher", display_name="Other Teacher")

        conflicting_user = User.objects.create_user(username="demo_student_anna", password="pass")
        UserProfile.objects.create(user=conflicting_user, role="student", display_name="Conflicting")
        TeacherStudent.objects.create(teacher=other_teacher, student=conflicting_user)

        with self.assertRaisesRegex(CommandError, "not assigned to teacher"):
            call_command("seed_demo_lessons", "demo_teacher")

        # Verify no changes were made
        self.assertEqual(Lesson.objects.filter(teacher=self.teacher).count(), 0)
        self.assertEqual(TeacherStudent.objects.filter(teacher=self.teacher).count(), 0)

    def test_conflicting_username_no_profile(self):
        """Test that existing username without profile raises error."""
        from django.core.management import call_command
        from django.core.management.base import CommandError

        # Create user with demo username but no profile
        User.objects.create_user(username="demo_student_anna", password="pass")

        with self.assertRaisesRegex(CommandError, "has no profile"):
            call_command("seed_demo_lessons", "demo_teacher")

        # Verify no changes were made
        self.assertEqual(Lesson.objects.filter(teacher=self.teacher).count(), 0)
        self.assertEqual(TeacherStudent.objects.filter(teacher=self.teacher).count(), 0)

    def test_transaction_rollback_on_error(self):
        """Test that transaction rolls back when error occurs."""
        from django.core.management import call_command
        from django.core.management.base import CommandError

        # Create conflicting user BEFORE running seed command
        conflicting_user = User.objects.create_user(username="demo_student_bartek", password="pass")
        UserProfile.objects.create(user=conflicting_user, role="teacher", display_name="Conflicting")

        # Run command - should fail and roll back
        with self.assertRaisesRegex(CommandError, "not a student"):
            call_command("seed_demo_lessons", "demo_teacher")

        # Verify demo_student_anna was rolled back
        self.assertEqual(User.objects.filter(username="demo_student_anna").count(), 0)

        # Verify no demo lessons or assignments were created
        self.assertEqual(Lesson.objects.filter(teacher=self.teacher).count(), 0)
        self.assertEqual(TeacherStudent.objects.filter(teacher=self.teacher).count(), 0)

        # Verify conflicting Bartek account remains unchanged
        self.assertEqual(User.objects.filter(username="demo_student_bartek").count(), 1)
        self.assertEqual(conflicting_user.profile.role, "teacher")

    def test_demo_students_have_unusable_passwords(self):
        """Test that demo students have genuinely unusable passwords."""
        from django.core.management import call_command
        call_command("seed_demo_lessons", "demo_teacher")

        for username in ["demo_student_anna", "demo_student_bartek", "demo_student_carol"]:
            student = User.objects.get(username=username)
            self.assertFalse(student.has_usable_password())
