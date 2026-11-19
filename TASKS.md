# Web for Freelancers — Development Tasks

**Version:** 0.1  
**Status:** Planning  
**Current Phase:** Django Foundation

## Agent Execution Rules

- Read `AGENTS.md`, `PROJECT_SPEC.md`, and `ARCHITECTURE.md` before implementation.
- Complete only ONE task per request.
- Never start the next task automatically.
- Follow the approved architecture.
- Write or update relevant tests.
- Report modified files and test results.
- Ask for approval before introducing dependencies or changing architecture.
- Do not mark tasks complete without verification.

---

## Phase 0 — Project Preparation

- [x] **TASK-001:** Review project documentation for inconsistencies.
- [x] **TASK-002:** Verify `.gitignore` and local Aider configuration.
- [x] **TASK-003:** Establish the initial Git baseline.

**Acceptance criteria:** Documentation is consistent, unwanted files are ignored, and the repository has a clean committed baseline.

## Phase 1 — Django Foundation

- [x] **TASK-004:** Initialize Django project and configuration.
- [x] **TASK-005:** Configure SQLite and initial migrations.
- [ ] **TASK-006:** Create shared base HTML template and local static CSS.
- [ ] **TASK-007:** Create responsive landing page with Teacher and Student sections.

**Acceptance criteria:** The application starts locally, Django system checks pass, and the landing page renders correctly.

## Phase 2 — Authentication

- [ ] **TASK-008:** Implement UserProfile model with Teacher and Student roles.
- [ ] **TASK-009:** Implement Teacher login.
- [ ] **TASK-010:** Implement Student login.
- [ ] **TASK-011:** Implement role-based authorization and secure POST logout.
- [ ] **TASK-012:** Create fictional Teacher and Student demo accounts using a local management command.

**Acceptance criteria:** Both roles can authenticate, access their own dashboards, and cannot access restricted pages.

## Phase 3 — Teacher Dashboard

- [ ] **TASK-013:** Create Teacher Dashboard layout and sidebar.
- [ ] **TASK-014:** Implement TeacherStudent relationship.
- [ ] **TASK-015:** Implement Lesson model and relationship validation.
- [ ] **TASK-016:** Add fictional students and lessons.
- [ ] **TASK-017:** Display scheduled lessons in the dashboard table.
- [ ] **TASK-018:** Display stored Microsoft Teams meeting URLs.
- [ ] **TASK-019:** Add Lessons, Students, Homework and Notes placeholder pages.

**Acceptance criteria:** A logged-in teacher sees their own scheduled lessons, students, topics, dates and meeting URLs. Teacher data is isolated.

## Phase 4 — Student Dashboard

- [ ] **TASK-020:** Create basic Student Dashboard.
- [ ] **TASK-021:** Display student welcome information.
- [ ] **TASK-022:** Verify Student navigation and access restrictions.

**Acceptance criteria:** Students can log in and access their dashboard without accessing teacher-only content.

## Phase 5 — Testing and Quality

- [ ] **TASK-023:** Review and complete authentication tests.
- [ ] **TASK-024:** Test role-based authorization and data isolation.
- [ ] **TASK-025:** Test lesson relationships and dashboard rendering.
- [ ] **TASK-026:** Review responsive layout and accessibility.
- [ ] **TASK-027:** Run the complete test suite and resolve failures.

**Acceptance criteria:** Relevant tests pass, Django system checks pass, and known limitations are documented.

## Phase 6 — MVP Completion

- [ ] **TASK-028:** Update README with installation and setup instructions.
- [ ] **TASK-029:** Review documentation for accuracy.
- [ ] **TASK-030:** Perform manual acceptance testing of the complete Teacher and Student flows.

**Acceptance criteria:** The local demo works without paid APIs or external services and can be demonstrated to a real user using fictional data.

---

## Future Backlog — Not Approved

- Teacher-generated student registration invitations.
- Homework management.
- Lesson notes and history.
- Administrative automation.
- Optional language practice exercises.
- Additional features discovered through user research.

These features must not be implemented until explicitly approved.

---

## Current Task

**TASK-006 — Create shared base HTML template and local static CSS.**

Do not implement application code during this task.

## Definition of Done

A task is complete only when:

1. The requested changes are implemented.
2. Relevant tests or checks have been executed.
3. Results and limitations are reported.
4. No unrelated functionality was changed.
5. The developer has reviewed and approved the result.
