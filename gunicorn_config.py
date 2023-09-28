import multiprocessing

# Django WSGI application path in pattern MODULE_NAME:VARIABLE_NAME
wsgi_app = "developer_site.wsgi:application"
# The socket to bind
bind = "0.0.0.0:8000"
# The number of worker processes for handling requests
workers = multiprocessing.cpu_count() * 2 + 1
timeout = 600
