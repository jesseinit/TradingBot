import logging

from binance.exceptions import BinanceAPIException
from flask import Flask, jsonify
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from opencensus.ext.azure.log_exporter import AzureLogHandler
from werkzeug.exceptions import HTTPException

from config import config as app_config
from decouple import config

logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(
    connection_string=f"InstrumentationKey={config('INSTRUMENTATION_KEY')}"))
logger.setLevel(logging.DEBUG)

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()


def create_app(config_name: str = "developement"):
    """Application factory
    Args:
        config_name (str): the application config name to determine which env to run on
    Returns:
        The Flask application object
    """

    app = Flask(__name__)
    app.config.from_object(app_config[config_name])
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    from blueprints.listener.listener_blueprint import listener_blueprint
    from blueprints.wallet.wallet_blueprint import wallet_blueprint

    app.register_blueprint(wallet_blueprint)
    app.register_blueprint(listener_blueprint)

    @app.errorhandler(BinanceAPIException)
    def handle_binance_exception(error):
        """Error handler called when a BinanceAPIException Exception is raised"""
        from utils.mail_helper import MailHelper
        MailHelper.send_exception_mail(error.message)
        return {"message": error.message, "code": error.code}, getattr(error, 'status_code', 500)

    def handle_error(error):
        code = 500
        if isinstance(error, HTTPException):
            code = error.code
        return jsonify(error='error', code=code)

    for cls in HTTPException.__subclasses__():
        app.register_error_handler(cls, handle_error)

    @app.route("/")
    def hello_world():
        return "<p>Hello Carina, what do you want to do today?</p>"

    return app
