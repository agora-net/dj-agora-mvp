---
description: Agora project guidelines for AI agents
version: 2.0
tags: ["agora", "project", "core-behavior"]
---

# AI Agent Instructions

## Build/Lint/Test Commands

- `just test-backend` - run all tests
- `just test-backend app.tests.test_file.TestClass.test_method` - run single test
- `just lint-backend` - lint with ruff
- `just format-backend` - format with ruff
- `just manage makemigrations` - create migrations
- `uv run python manage.py shell` - Django shell

## Code Style

- **Formatting**: ruff format, 100 char limit, trailing commas
- **Imports**: absolute imports, sorted by ruff, no relative imports
- **Naming**: snake_case (functions/vars), PascalCase (classes), UPPER_CASE (constants)
- **Types**: use type hints, Optional[Type] over Type | None, named args with `*`
- **Docstrings**: Google-style, multiline with """
- **Error handling**: specific exceptions, proper logging, graceful degradation

## Security First

- Never expose secrets (Keycloak, Ondato, Stripe)
- Validate all inputs server-side with nh3 sanitization
- Use HTTPS only, proper CORS, CSRF protection
- Store credentials in environment variables only

## Project Structure

- Apps: `agora/apps/`
- Tests: `tests/` within each app
- Static: `static/` and `staticfiles/`
- Templates: `templates/`
- Config: `config/` directory

## Git Workflow

- Branch naming: `feature/name` or `bug/name`
- Follow conventional commits from `.cursor/rules/conventional-commit.mdc`
- Run `just lint-backend && just format-backend` before commits
