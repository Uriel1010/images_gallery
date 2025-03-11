# Gunicorn configuration file for production
bind = "0.0.0.0:5000"
workers = 4
accesslog = "-"
errorlog = "-"
timeout = 120
