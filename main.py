from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config


db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name: str):
    """Application factory
    Args:
        config_name (str): the application config name to determine which env to run on
    Returns:
        The Flask application object
    """

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)
    migrate.init_app(app, db)

    from blueprints.listener.listener_blueprint import listener_blueprint
    from blueprints.wallet.wallet_blueprint import wallet_blueprint

    app.register_blueprint(wallet_blueprint)
    app.register_blueprint(listener_blueprint)

    @app.route("/")
    def hello_world():
        return "<p>Hello Carina, what do you want to do today?</p>"

    return app
