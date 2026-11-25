# Web for Freelancers — Architecture

**Version:** 0.1  
**Status:** Implemented local prototype

**Architecture:** Django Monolith

## 1. Architecture Overview

The application uses a traditional server-rendered Django architecture.

The initial prototype runs locally without external services.

**Request flow:**

Browser → Django URL Router → View → Models → SQLite

Django Templates render HTML responses.

No separate frontend server, microservices, or REST API are required for version 0.1.

## 2. Technology Stack

| Layer | Technology |
|---|---|
| Language | Python |
| Backend | Django 5.2.19 LTS |
| Database | SQLite |
| Frontend | Django Templates, HTML, CSS |
| Interactivity | Vanilla JavaScript when necessary |
| Authentication | Django built-in authentication |
| Testing | Django TestCase |
| Development | Local environment |
| Version Control | Git / GitHub |

Use a currently supported Django version with compatible Python dependencies.

## 3. Project Structure

```text
web-for-freelancers/
├── AGENTS.md
├── PROJECT_SPEC.md
├── ARCHITECTURE.md
├── TASKS.md
├── README.md
├── .gitignore
├── requirements.txt
├── manage.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── migrations/
│   ├── management/commands/seed_demo_accounts.py
│   └── tests.py
│
├── lessons/
│   ├── models.py
│   ├── migrations/
│   ├── management/commands/seed_demo_lessons.py
│   └── tests.py
│
├── templates/
│   ├── base.html
│   ├── landing.html
│   └── accounts/
│
└── static/
    └── css/style.css
```

The tree shows the main application files. `accounts` owns authentication and both dashboards. `lessons` owns lesson and assignment data.

## 4. User Roles

The system supports two roles:

**Teacher**
- Access teacher dashboard.
- View their own upcoming lessons and the student shown for each lesson.
- Access the Lessons, Students, Homework, and Notes placeholder pages.

**Student**
- Access the welcome dashboard and log out.
- Cannot access teacher-only pages.
- Cannot access another student's private records.

Use Django's built-in User model and a related profile containing the user role.

## 5. Data Models

### UserProfile
- `user` is a `OneToOneField` to Django User, with reverse accessor `profile`.
- `role` is a `CharField` with a 10-character maximum and `teacher` and `student` choices.
- `display_name` is a `CharField` with a 100-character maximum and allows blanks.

### TeacherStudent
- `teacher` is a `ForeignKey` to User, with reverse accessor `taught_students`.
- `student` is a `OneToOneField` to User, with reverse accessor `assigned_teacher`.

A teacher can have many students. A student can have zero or one teacher assignment. The one-to-one field enforces uniqueness in the database. Model validation requires distinct users with the corresponding roles.

### Lesson
- `teacher` and `student` are `ForeignKey` fields to User, with reverse accessors `taught_lessons` and `student_lessons`.
- `topic` is a `CharField` with a 200-character maximum.
- `scheduled_at` is a `DateTimeField` and determines the default ordering.
- `duration_minutes` is a `PositiveIntegerField`.
- `meeting_url` is a `URLField` that allows blank and null values.

Model validation requires a nonblank topic, a duration greater than zero, the corresponding user roles, and an existing assignment between the student and the teacher. All user relationships listed here cascade on deletion.

Future models for homework, notes and invitations are not implemented yet.

## 6. Routes

| URL | Django route name | Purpose |
|---|---|---|
| `/` | `landing` | Teacher / Student selection |
| `/accounts/teacher/login/` | `teacher_login` | Teacher login |
| `/accounts/student/login/` | `student_login` | Student login |
| `/accounts/logout/` | `logout` | Logout via POST, then return to the landing page |
| `/accounts/teacher/dashboard/` | `teacher_dashboard` | Teacher dashboard |
| `/accounts/student/dashboard/` | `student_dashboard` | Student dashboard |
| `/accounts/teacher/lessons/` | `teacher_lessons` | Lessons placeholder |
| `/accounts/teacher/students/` | `teacher_students` | Students placeholder |
| `/accounts/teacher/homework/` | `teacher_homework` | Homework placeholder |
| `/accounts/teacher/notes/` | `teacher_notes` | Notes placeholder |
| `/admin/` | `admin:index` | Django admin |

## 7. Authentication and Security

- Use session-based authentication.
- Store passwords using Django's password hashing.
- Enable CSRF protection.
- Enforce authorization in backend views.
- Use POST for logout.
- Validate redirects and meeting URLs.
- Prevent student access to teacher-only pages.
- Filter teacher data by authenticated teacher.
- Use fictional accounts and records during development.
- Never commit environment secrets, credentials or the development database.

## 8. User Interface

Use a shared base template for consistency.

**Landing Page**
- Two responsive role selection panels.

**Authentication**
- Separate Teacher and Student login screens.

**Teacher Dashboard**
- Shared sidebar across the dashboard and teacher placeholders.
- Upcoming lessons table filtered to the signed-in teacher and sorted by scheduled time.
- Student display name or username, topic, date and time, duration, and an optional stored meeting link.

**Student Dashboard**
- Basic welcome view and logout.

Use locally served CSS and JavaScript. Do not depend on CDN assets.

## 9. Testing Strategy

Write automated tests covering:

- Teacher and Student authentication.
- Invalid login credentials.
- Role-based access restrictions.
- Unauthorized dashboard access.
- Teacher data isolation.
- Lesson relationship validation.
- Dashboard rendering.
- Logout behavior.

Tests must not depend on external APIs.

## 10. Future Architecture

Potential future capabilities:

- Secure teacher-generated student invitation links.
- Homework management.
- Lesson notes and history.
- Administrative automation.
- Multiple independent teachers.

These features are not part of the initial implementation.

## 11. Architectural Principles

1. Start with a modular Django monolith.
2. Avoid premature abstractions.
3. Use built-in Django capabilities whenever possible.
4. Keep business logic separate from presentation.
5. Prioritize secure data access.
6. Add complexity only when product requirements justify it.
7. Implement and test incrementally.