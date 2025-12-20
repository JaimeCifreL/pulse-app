release: python manage.py migrate --noinput
web: daphne -b 0.0.0.0 -p $PORT pulse_backend.asgi:application
worker: celery -A pulse_backend worker --pool=solo
beat: celery -A pulse_backend beat
