web: gunicorn routing.wsgi
release: python manage.py migrate
worker: python -u run-worker.py