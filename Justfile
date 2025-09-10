_default:
    @just --list

# Install lefthook
install-lefthook:
    @uv run lefthook install

# Install the development dependencies
install-dev:
    @uv sync

# Create new database migrations
makemigrations:
    @uv run python manage.py makemigrations

# Apply database migrations
migrate:
    @uv run python manage.py migrate

# Run the development server
runserver:
    @uv run python manage.py runserver

# Run the frontend hot reload
[working-directory: "frontend/@agora/agora"]
dev-frontend:
    @pnpm dev

# Test the backend code
test-backend *ARGS:
    @uv run python manage.py test {{ARGS}}

# Shortcut for manage.py commands
manage *ARGS:
    @uv run python manage.py {{ARGS}}

# Collect static files
collectstatic:
    @uv run python manage.py collectstatic --noinput

# Lint the frontend code

# Lint the backend code
lint-backend:
    @uv run ruff check --fix

# Format the backend code
format-backend:
    @uv run ruff format

# Format the frontend code
