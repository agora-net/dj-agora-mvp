_default:
    @just --list

# Shortcut for manage.py commands
manage *ARGS:
    @uv run python manage.py {{ARGS}}

# Run the Django shell with IPython
shell $IPYTHONDIR="./.ipython":
    @just manage shell
    
# Install lefthook
install-lefthook:
    @uv run lefthook install

# Install the development dependencies
install-dev:
    @uv sync

# Create new database migrations
makemigrations:
    @just manage makemigrations

# Apply database migrations
migrate:
    @just manage migrate

# Run the development server
runserver:
    @uv run gunicorn --reload --log-level debug --workers 1 --bind 0.0.0.0:8000 --worker-tmp-dir /tmp --config config/gunicorn/gunicorn.conf.py agora.wsgi:application

# Run the frontend hot reload
[working-directory: "frontend/@agora/agora"]
dev-frontend:
    @pnpm dev

# Test the backend code
test-backend *ARGS:
    @just manage test {{ARGS}}

# Collect static files
collectstatic:
    @just manage collectstatic --noinput

# Lint the frontend code

# Lint the backend code
lint-backend:
    @uv run ruff check --fix

# Format the backend code
format-backend:
    @uv run ruff format

# Format the frontend code
