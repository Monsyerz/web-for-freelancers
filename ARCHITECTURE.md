# Web for Freelancers — Architecture

**Version:** 0.1  
**Status:** Proposed  
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
| Backend | Django |
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
│   └── tests.py
│
├── lessons/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── dashboard/
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── templates/
│   ├── base.html
│   ├── landing.html
│   ├── accounts/
│   └── dashboard/
│
└── static/
    ├── css/
    └── js/
```

This is the intended structure, not a requirement to create every file immediately.

## 4. User Roles

The system supports two roles:

**Teacher**
- Access teacher dashboard.
- View assigned students.
- View their own scheduled lessons.
- Access teacher navigation pages.

**Student**
- Access student dashboard.
- Cannot access teacher-only pages.
- Cannot access another student's private records.

Use Django's built-in User model and a related profile containing the user role.

## 5. Initial Data Models

### UserProfile
- user: OneToOne relationship with Django User
- role: Teacher / Student
- display_name

### TeacherStudent
- teacher: ForeignKey to User
- student: ForeignKey to User

For v0.1, a student is associated with one teacher. Enforce this through a database uniqueness constraint on the student.

### Lesson
- teacher: ForeignKey to User
- student: ForeignKey to User
- topic: CharField
- scheduled_at: DateTimeField
- duration_minutes: PositiveIntegerField
- meeting_url: URLField, optional

Validate that each lesson's student belongs to the specified teacher.

Future models for homework, notes and invitations are not implemented yet.

## 6. Routes

| URL | Purpose |
|---|---|
| `/` | Teacher / Student selection |
| `/accounts/teacher/login/` | Teacher login |
| `/accounts/student/login/` | Student login |
| `/accounts/logout/` | Logout (POST) |
| `/dashboard/teacher/` | Teacher dashboard |
| `/dashboard/student/` | Student dashboard |
| `/lessons/` | Teacher lessons |
| `/students/` | Teacher student list |
| `/homework/` | Placeholder |
| `/notes/` | Placeholder |

Final route names should be consistent and use Django's named URL patterns.

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
- Persistent sidebar.
- Main lesson table.
- Student, topic, date/time and Teams link.

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