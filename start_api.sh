#!/bin/bash 

echo "!!!Starting Application!!!"

echo ">>>Running DB Migrations>>>"
flask db upgrade
echo "<<<DB Migrations Done>>>"

celery -A celery_worker.celery worker --loglevel=INFO &

echo ">>>Starting Application Server>>>"
# flask run -p 8000
gunicorn wsgi:app -b 0.0.0.0 -w 4 --access-logfile - --error-logfile -
