<<<<<<< HEAD
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:" + os.getenv("PORT", "5000")
backlog = 2048

# Worker processes
workers = 2  # Reduced number of workers for Render
worker_class = 'gevent'
worker_connections = 1000
timeout = 120  # 2 minutes timeout
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
graceful_timeout = 30

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Process naming
proc_name = 'gunicorn_gotomeeting'

# SSL
keyfile = None
certfile = None 
=======
bind = "0.0.0.0:10000"
workers = 1
timeout = 600
keepalive = 300
worker_class = "gevent"
worker_connections = 1000
max_requests = 100
max_requests_jitter = 10
graceful_timeout = 600 
>>>>>>> 94f3a3c35c049619c79057ac72e28be3cea66f1d
