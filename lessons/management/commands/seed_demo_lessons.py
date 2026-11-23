from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from datetime import timedelta

from accounts.models import UserProfile
from lessons.models import TeacherStudent, Lesson

User = get_user_model()

DEMO_STUDENTS = [
    {"username": "demo_student_anna", "display_name": "Anna Kowalska"},
    {"username": "demo_student_bartek", "display_name": "Bartek Nowak"},
    {"username": "demo_student_carol", "display_name": "Carol Smith"},
]

DEMO_LESSONS = [
    {"topic": "Grammar: Present Perfect", "duration": 60, "offset_hours": 2},
    {"topic": "Vocabulary: Business English", "duration": 45, "offset_hours": 4},
    {"topic": "Speaking: Job Interview Practice", "duration": 60, "offset_hours": 6},
    {"topic": "Reading: News Articles", "duration": 45, "offset_hours": 8},
    {"topic": "Writing: Email Etiquette", "duration": 60, "offset_hours": 10},
]


class Command(BaseCommand):
    help = "Seed the database with fictional students and lessons for a teacher."

    def add_arguments(self, parser):
        parser.add_argument(
            "teacher_username",
            type=str,
            help="Username of the teacher to assign demo students and lessons to."
        )

    def handle(self, *args, **options):
        teacher_username = options["teacher_username"]

        # Validate teacher exists and has TEACHER role
        try:
            teacher = User.objects.get(username=teacher_username)
        except User.DoesNotExist:
            raise CommandError(f"Teacher '{teacher_username}' does not exist.")

        try:
            profile = teacher.profile
            if profile.role != UserProfile.Role.TEACHER:
                raise CommandError(f"User '{teacher_username}' does not have TEACHER role.")
        except UserProfile.DoesNotExist:
            raise CommandError(f"Teacher '{teacher_username}' has no profile.")

        with transaction.atomic():
            # Create or get demo students
            students = []
            for student_data in DEMO_STUDENTS:
                username = student_data["username"]
                display_name = student_data["display_name"]

                # Check if username already exists
                try:
                    student = User.objects.get(username=username)
                except User.DoesNotExist:
                    # Create new student with unusable password
                    student = User.objects.create_user(
                        username=username,
                        password=None
                    )
                    UserProfile.objects.create(
                        user=student,
                        role=UserProfile.Role.STUDENT,
                        display_name=display_name
                    )
                    self.stdout.write(self.style.SUCCESS(f"Created student: {username}"))
                else:
                    # Username exists - validate it's a student assigned to this teacher
                    try:
                        student_profile = student.profile
                        if student_profile.role != UserProfile.Role.STUDENT:
                            raise CommandError(
                                f"Username '{username}' exists but is not a student."
                            )
                        # Check if already assigned to this teacher
                        try:
                            TeacherStudent.objects.get(
                                teacher=teacher,
                                student=student
                            )
                        except TeacherStudent.DoesNotExist:
                            raise CommandError(
                                f"Username '{username}' exists but is not assigned to teacher '{teacher_username}'."
                            )
                    except UserProfile.DoesNotExist:
                        raise CommandError(
                            f"Username '{username}' exists but has no profile."
                        )

                students.append(student)

            # Assign students to teacher (only for newly created students)
            for student in students:
                TeacherStudent.objects.get_or_create(
                    teacher=teacher,
                    student=student
                )

            # Create demo lessons
            for lesson_data in DEMO_LESSONS:
                scheduled_at = timezone.now() + timedelta(hours=lesson_data["offset_hours"])
                lesson, created = Lesson.objects.get_or_create(
                    teacher=teacher,
                    topic=lesson_data["topic"],
                    defaults={
                        "student": students[0],
                        "scheduled_at": scheduled_at,
                        "duration_minutes": lesson_data["duration"]
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created lesson: {lesson.topic}"))

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
