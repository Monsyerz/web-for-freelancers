# AGENTS.md — Web for Freelancers

## Project Mission
Build a simple, maintainable web application for freelance professionals, initially focused on private language teachers.

The first version is a local prototype, not a production SaaS.

## Technology Rules
- Backend: Python and Django.
- Database: SQLite for local development.
- Frontend: Django Templates, HTML, CSS and vanilla JavaScript.
- No React for the initial version.
- Use free and open-source dependencies only.
- No paid APIs, subscription services, cloud AI APIs or external CDNs.
- The application must work locally without third-party services.

## Agent Workflow
1. Read the project specification before implementing anything.
2. Inspect existing code before modifying it.
3. Explain the proposed changes before significant modifications.
4. Implement only the currently assigned task.
5. Prefer small, incremental changes over large rewrites.
6. Do not introduce features outside the approved scope.
7. Ask for approval before introducing new dependencies or architectural changes.
8. Never remove working functionality without permission.
9. Never attempt to implement the entire application in a single task.
10. Keep generated responses short and avoid exceeding model output limits.

## Code Quality
- Follow Python PEP 8 conventions.
- Use Django's established patterns.
- Keep functions and classes focused.
- Avoid unnecessary abstraction and overengineering.
- Write maintainable, readable code.
- Add automated tests for important functionality.
- Never hardcode credentials or secrets.
- Use Django's authentication, authorization and CSRF protections.

## Data and Security
- Use fictional data during development.
- Never commit secrets, passwords or environment files.
- Respect Teacher and Student permissions.
- A student must never access another student's private data.
- Do not implement payments or external integrations without approval.

## Completion Requirements
After each task:
- Summarize files created or modified.
- Report tests executed and their results.
- Explain any remaining limitations.
- Update TASKS.md when appropriate.
- Do not claim something works unless it has been verified.

## Product Principle
Solve actual user problems. Prioritize usability, simplicity and reducing administrative work over adding unnecessary features.

## Git & Review Policy

1. Never create Git commits without explicit developer approval.
2. Never push, merge, rebase or delete branches without explicit approval.
3. Show the developer a summary of all modified files after each task.
4. All changes must be reviewed before committing.
5. Implement new features on dedicated feature branches once the branching workflow is enabled.
6. Codex will independently review code changes and run relevant tests before approval.
7. The developer performs final manual verification before merging.
8. Never merge unreviewed changes into main.
9. Keep main stable and functional.
10. Do not mark tasks as complete until the required review and acceptance criteria pass.