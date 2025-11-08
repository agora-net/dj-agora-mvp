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

# Run the stripe CLI to listen for webhook events and forward them to the local server
stripe-webhook:
    @stripe listen --forward-to https://app.local.agora.gdn/webhooks/v1/stripe/ --skip-verify

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
runserver $GUNICORN_RELOAD="1":
    @uv run gunicorn --log-level debug --workers 1 --bind 0.0.0.0:8000 --worker-tmp-dir /tmp --config config/gunicorn/gunicorn.conf.py agora.wsgi:application

# Run the frontend hot reload
[working-directory: "frontend/@agora/agora"]
dev-frontend *ARGS:
    @pnpm dev {{ARGS}}

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
