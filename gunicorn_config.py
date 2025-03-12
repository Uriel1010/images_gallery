# Gunicorn configuration file

# Bind to all interfaces on port 5000.
bind = "0.0.0.0:5000"

# Number of worker processes.
workers = 4

# Log access and errors to stdout.
accesslog = "-"
errorlog = "-"

# Set a timeout (in seconds) for workers.
timeout = 120
