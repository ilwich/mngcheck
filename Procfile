release: python manage.py migrate
web: gunicorn mngcheck.wsgi
worker: /usr/local/bin/celery -A mngcheck worker -P solo
beat: /usr/local/bin/celery beat -A mngcheck -linfo

