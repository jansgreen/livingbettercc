web: gunicorn livingbettercc.wsgi --log-file - --timeout 120
release: python manage.py migrate --fake-initial --noinput
