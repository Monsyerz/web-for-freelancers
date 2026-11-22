from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from accounts.models import UserProfile
from lessons.models import TeacherStudent

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
