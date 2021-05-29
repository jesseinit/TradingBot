#!/bin/bash 

echo "!!!Starting Application!!!"

echo ">>>Running DB Migrations>>>"
flask db upgrade
echo "<<<DB Migrations Done>>>"

celery -A celery_worker.celery worker &

echo ">>>Starting Application Server>>>"
# flask run -p 8000
gunicorn wsgi:app -w 4 -b 0.0.0.0
