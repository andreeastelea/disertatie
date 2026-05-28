# Gunicorn production configuration
import multiprocessing
import os

backend_port = os.environ.get("BACKEND_PORT", "5000")
bind = f"0.0.0.0:{backend_port}"

# 2 workers per CPU core is a common starting point for mixed workloads
workers = multiprocessing.cpu_count() * 2 + 1

# Use sync worker (default) — suitable for CPU-bound + I/O-bound comparison
worker_class = "sync"

# Allow more time for CPU-bound requests
timeout = 120

# Recycle workers after N requests to avoid memory leaks
max_requests = 1000
max_requests_jitter = 100

accesslog = "-"
errorlog = "-"
loglevel = "info"
