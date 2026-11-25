# Web for Freelancers

Web for Freelancers is a web application designed to reduce administrative work for independent professionals. The first version (v0.1) focuses on language teachers and their students.

## MVP Functionality

- Landing page with role selection (Teacher / Student)
- Teacher and student login
- Teacher dashboard with upcoming lessons
- Student dashboard with welcome information
- Teacher dashboard navigation (Lessons, Students, Homework, Notes) (placeholder pages)
- Logout

## Technology Stack

- Backend: Python, Django 5.2.19 LTS
- Frontend: HTML, CSS, Django Templates, vanilla JavaScript
- Database: SQLite
- Authentication: Django built-in authentication

## Requirements

- Python 3.10–3.14
- Git
- Git Bash on Windows, or Bash on macOS or Linux

## Installation and Configuration

### 1. Clone the repository

```bash
git clone https://github.com/Monsyerz/web-for-freelancers.git
cd web-for-freelancers
```

### 2. Create a virtual environment

```bash
python -m venv .venv
# Windows (Git Bash)
source .venv/Scripts/activate

# macOS or Linux (Bash)
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run database migrations

```bash
python manage.py migrate
```

### 5. Create demo accounts

Set environment variables with placeholder passwords (do not use real passwords):

```bash
export DEMO_TEACHER_PASSWORD="placeholder_teacher_password"
export DEMO_STUDENT_PASSWORD="placeholder_student_password"
```

Create demo accounts:

```bash
python manage.py seed_demo_accounts
```

Default accounts:
- Teacher: `demo_teacher`
- Student: `demo_student`

### 6. Create demo lessons

```bash
python manage.py seed_demo_lessons demo_teacher
```

The command creates five upcoming lessons on a fresh database. Rerunning it keeps existing lesson dates. Once those lessons have passed, they disappear from the upcoming lessons table.

## Running the server

```bash
python manage.py runserver
```

The application will be available at: http://127.0.0.1:8000/

## Logging in

- Teacher: http://127.0.0.1:8000/accounts/teacher/login/
- Student: http://127.0.0.1:8000/accounts/student/login/

## Testing

### Django system check

```bash
python manage.py check
```

### Run automated tests

```bash
python manage.py test
```

## Limitations

- The application runs locally and is not production-ready
- Uses fictional demo data
- Does not include public registration
- Does not include password reset
- Does not include integration with external services
- Students created by `seed_demo_lessons` cannot log in, unlike `demo_student`
- Stored Microsoft Teams URLs can be displayed, but are not generated automatically or populated by the seed command
- Rerunning seed_demo_accounts does not reset existing account passwords.

## Out-of-scope features (not implemented)

- Teacher invitation system
- Homework management
- Lesson notes and history
- Administrative automation
- Language practice exercises
- Payments and subscriptions
- Microsoft Teams API integration
- Public registration
- Password reset
- Production hosting
