#!/usr/bin/env bash
# start-server.sh
export DEBUG=false
python manage.py migrate
python manage.py loaddata seeddata/*.json
if  [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    (python manage.py createsuperuser --noinput)
fi
chmod -R 777 db
chown -R www-data:www-data db
python ./manage.py collectstatic
mkdir -p /home/staticfiles
mv static_root/* /home/staticfiles
rm -rf static_root/

if [ $AUTOSCALING_ENABLED == true ]
then 
    echo "autoscaling enabled, will only run telemetry queue"
    (celery -A app worker --concurrency=2 -n telemetryNode -l INFO --purge) &
else 
    (celery -A app worker --concurrency=2 -n telemetryNode -l INFO --purge) &
    echo "autoscaling disabled, will run everything"
fi

(celery -A app beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler) &

gunicorn app.wsgi --reload --user www-data --bind 0.0.0.0:8000 --workers 3 --timeout 300
