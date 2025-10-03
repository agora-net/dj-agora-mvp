# Load the autoreload extension
get_ipython().run_line_magic("load_ext", "autoreload")  # type: ignore  # noqa: F821
# Enable autoreload mode 2 (reload all modules)
get_ipython().run_line_magic("autoreload", "2")  # type: ignore # noqa: F821

print("Autoreload is enabled. Modules will be reloaded before execution.")
