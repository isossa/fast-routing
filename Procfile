web: daphne -p $PORT --bind 0.0.0.0 routing.asgi:application
release: python manage.py migrate
worker: python manage.py runworker