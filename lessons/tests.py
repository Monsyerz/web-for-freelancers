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
