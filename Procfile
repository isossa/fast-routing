web: daphne -b 0.0.0.0 -p $PORT routing.asgi:application
release: python manage.py migrate
worker: python manage.py runworker