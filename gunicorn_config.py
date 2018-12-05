import os

workers = int(os.environ.get('GUNICORN_PROCESSES', 2))
threads = int(os.environ.get('GUNICORN_THREADS', '5'))
