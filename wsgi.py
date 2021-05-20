import os
from main import create_app
from decouple import config


app = create_app(config("FLASK_ENV"))
app.app_context().push()

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
