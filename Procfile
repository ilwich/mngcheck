release: python manage.py migrate
web: gunicorn mngcheck.wsgi
worker: celery -A mngcheck worker -P solo
beat: celery -A mngcheck beat -linfo

