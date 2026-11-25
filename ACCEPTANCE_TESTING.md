# TASK-030 — Manual Acceptance Testing

**Date:** November 25, 2026

**Branch:** `docs/mvp-completion`

**Status:** Pending remaining manual checks and developer approval

## Confirmed manual results

| Check | Result |
|---|---|
| Teacher and Student login | PASS |
| Teacher and Student dashboards | PASS |
| Empty lesson schedule | PASS |
| Upcoming lesson rendering | PASS |
| Stored Microsoft Teams URL display and opening | PASS |
| Student access to the Teacher Dashboard returns HTTP 403 | PASS |
| Anonymous access redirects to login | PASS |
| Mobile dashboard and horizontal table scrolling | PASS with UX limitations |

On mobile, the lesson table could be scrolled horizontally. The mobile table layout remains a proposed improvement in [BACKLOG.md](BACKLOG.md).

## Reported automated verification

| Check | Result |
|---|---|
| Full test suite | 109/109 passed in 91.485 seconds |
| Django system check | Zero issues |
| `git diff --check` | Passed |
| Working tree before documentation changes | Clean |

## Manual checks pending developer confirmation

- Confirm that the landing page renders correctly and both role buttons lead to their respective login pages.
- From the Teacher Dashboard, confirm that the Lessons, Students, Homework, and Notes links open the intended placeholders and that the Dashboard link returns to the dashboard.
- Confirm logout for both roles. Each should return to the landing page, and revisiting the dashboard should redirect to login.
- Confirm the local MVP can be demonstrated with fictional data and without reliance on paid APIs or cloud services for the core flows.

Leave TASK-030 unchecked until all acceptance criteria are confirmed and the developer approves completion.
