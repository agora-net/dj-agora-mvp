_default:
    @just --list

# Create new database migrations
makemigrations:
    @uv run python manage.py makemigrations

# Apply database migrations
migrate:
    @uv run python manage.py migrate

# Run the development server
runserver:
    @uv run python manage.py runserver

# Shortcut for manage.py commands
manage *ARGS:
    @uv run python manage.py {{ARGS}}

# Lint the frontend code

# Lint the backend code
lint-backend:
    @uv run ruff check --fix

# Format the backend code
format-backend:
    @uv run ruff format

# Format the frontend code
