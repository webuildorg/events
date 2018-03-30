import os
import multiprocessing
workers = int(os.environ.get('GUNICORN_PROCESSES', multiprocessing.cpu_count()))
threads = int(os.environ.get('GUNICORN_THREADS', 4))

forwarded_allow_ips = '*'
secure_scheme_headers = {'X-Forwarded-Proto': 'https'}
