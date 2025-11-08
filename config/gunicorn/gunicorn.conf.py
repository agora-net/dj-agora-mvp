import glob
import multiprocessing
import os

bind = "unix:/run/gunicorn_mvp.sock"
workers = multiprocessing.cpu_count() * 2 + 1
loglevel = "warning"

# A directory to store temporary files.
# This helps keep /tmp clean and gives Gunicorn a private space.
worker_tmp_dir = "/dev/shm"

# The number of seconds a worker can remain idle before it's restarted.
# This can help free up memory on long-running processes.
timeout = 10

# The maximum number of requests a worker will process before restarting.
# This is a key memory management strategy. It helps prevent memory leaks.
max_requests = 1000
max_requests_jitter = 150

errorlog = "-"  # Log errors to stderr, where they'll be captured by journalctl.
accesslog = "-"  # Log access requests to stdout, also captured by journalctl.

if os.environ.get("GUNICORN_RELOAD") == "1":
    reload = True
    reload_engine = "auto"
    reload_extra_files = (
        glob.glob("agora/templates/**/*.html", recursive=True)
        + glob.glob("agora/apps/**/templates/**/*.html", recursive=True)  # app templates
        + glob.glob("templates/**/*.html", recursive=True)  # project templates
    )

    print(f"Reloading on static file changes: {reload_extra_files}")
