# Web for Freelancers — Project Specification

**Version:** 0.1  
**Status:** Prototype / Product Discovery

## 1. Project Overview

Web for Freelancers is a web application designed to reduce administrative work for independent professionals.

The initial prototype focuses on freelance language teachers and their students.

The product's long-term functionality will be determined through research with a real freelance language teacher.

## 2. Project Goals

- Create a functional local web application.
- Provide separate Teacher and Student experiences.
- Simplify access to lesson information.
- Establish a foundation for future administrative tools.
- Keep the application easy to use and maintain.

## 3. Technology Stack

- Backend: Python, Django 5.2.19 LTS
- Frontend: HTML, CSS, Django Templates, vanilla JavaScript
- Database: SQLite
- Authentication: Django built-in authentication
- External services: None required

All dependencies must be free and open source.

## 4. Landing Page

The landing page must contain two equally sized sections on desktop:

**Left: Teacher**
- Teacher icon
- Short description
- Login button

**Right: Student**
- Student icon
- Short description
- Login button

The layout must be responsive on mobile devices.

Each login button redirects to the appropriate login page.

## 5. Authentication

- Django session authentication supports Teacher and Student roles.
- Teachers sign in at `/accounts/teacher/login/` and default to `/accounts/teacher/dashboard/`.
- Students sign in at `/accounts/student/login/` and default to `/accounts/student/dashboard/`.
- Login forms and protected views enforce the required role.
- Both dashboards log out via a CSRF-protected POST to `/accounts/logout/` and return to the landing page.
- Use fictional accounts for local development.

Public registration is not included in version 0.1.

## 6. Teacher Dashboard

### Layout

A sidebar on the left and a main content area on the right.

### Sidebar Navigation

1. Dashboard
2. Lessons
3. Students
4. Homework
5. Notes
6. Logout

### Dashboard Content

The dashboard shows the signed-in teacher's upcoming lessons in chronological order.

| Field | Description |
|---|---|
| Student | Student's profile display name, falling back to username |
| Lesson Topic | Planned lesson topic |
| Date & Time | Scheduled meeting time |
| Duration (min) | Lesson duration in minutes |
| Meeting | Link to the stored URL, or “Not provided” when empty |

Existing Microsoft Teams meeting links can be stored as optional URLs.

No Microsoft Teams API integration.

### Additional Pages

Lessons, Students, Homework, and Notes are teacher-only placeholder pages linked from the sidebar.

Their full functionality will be designed after user research.

## 7. Student Dashboard

After successful login, students access a separate dashboard.

The version 0.1 student dashboard shows a welcome message using the profile display name or username and provides a logout button.

Additional student features are not part of the initial milestone.

## 8. Data Requirements

The initial database must support:

- Users
- User roles
- Teacher–student relationships
- Scheduled lessons with topics and durations
- Optional meeting URLs

In version 0.1, a student can be associated with at most one teacher and may temporarily have no teacher assigned.

Use fictional test records only.

## 9. Future Features — Not Approved for Implementation

### Teacher Invitation System

A teacher generates a unique registration link and sends it to a student.

The student registers through that link and is automatically associated with the correct teacher.

Other ideas awaiting user research:

- Homework management
- Lesson notes and history
- Administrative automation
- Optional language practice exercises

These features must not be implemented without explicit approval.

## 10. Out of Scope

The initial version must not include:

- Paid APIs
- Cloud AI integrations
- Subscription or payment processing
- Video conferencing functionality
- Third-party calendar synchronization
- Public account registration
- Password reset
- Production hosting
- React or complex frontend frameworks

## 11. Acceptance Criteria

Version 0.1 is complete when:

- The landing page renders correctly.
- Both login pages work.
- Teacher and Student demo accounts can authenticate.
- Unauthorized access is blocked.
- The Teacher Dashboard displays fictional lessons from the database.
- Meeting links open correctly.
- Sidebar navigation works.
- The Student Dashboard loads.
- Users can log out.
- Automated tests for the implemented functionality pass.
- The application runs locally without paid or cloud services.

## 12. Development Principles

- Implement one small task at a time.
- Do not expand scope without approval.
- Keep the codebase simple and maintainable.
- Verify functionality before marking a task complete.
- Prioritize real user needs over speculative features.
