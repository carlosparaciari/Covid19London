release: python manage.py migrate
web: gunicorn Covid19London.wsgi --log-file -
worker: celery worker --app Covid19London --beat  --loglevel info --without-gossip --without-mingle --without-heartbeat