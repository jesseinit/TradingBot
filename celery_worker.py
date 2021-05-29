from main import create_app
from decouple import config

app = create_app(config("FLASK_ENV"))
app.app_context().push()

from main import celery
