import logging
import os
from binance.exceptions import BinanceAPIException
from celery import Celery
from decouple import config
from flask import Flask
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from opencensus.ext.azure.log_exporter import AzureLogHandler

from config import config as app_config

ENV = config("FLASK_ENV", default="development")

os.makedirs(os.path.dirname('logs/'), exist_ok=True)
logger = logging.getLogger(__name__)
db_logger = logging.getLogger('sqlalchemy')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s | %(thread)d | %(levelname)s | %(message)s')
if ENV == "production":
    azure_handler = AzureLogHandler(
        connection_string=f"InstrumentationKey={config('INSTRUMENTATION_KEY')}")
    azure_handler.setFormatter(formatter)
    file_handler = logging.FileHandler('logs/all.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(azure_handler)
    logger.addHandler(file_handler)
    db_handler = logging.FileHandler('logs/db.log')
    db_handler.setLevel(logging.DEBUG)
    logging.getLogger('sqlalchemy').addHandler(db_handler)
else:
    log_handler = logging.FileHandler('logs/all.log')
    log_handler.setFormatter(formatter)
    db_handler = logging.FileHandler('logs/db.log')
    db_handler.setLevel(logging.DEBUG)
    db_logger.addHandler(db_handler)
    logger.addHandler(log_handler)

db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()
mail = Mail()
celery = Celery(__name__,
                result_backend=config("REDIS_URL"),
                broker=config("REDIS_URL"))


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
    ma.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    celery.conf.update(app.config)

    from blueprints.listener.listener_blueprint import listener_blueprint
    from blueprints.wallet.wallet_blueprint import wallet_blueprint

    app.register_blueprint(wallet_blueprint)
    app.register_blueprint(listener_blueprint)

    @app.errorhandler(BinanceAPIException)
    def handle_binance_exception(error):
        """Error handler called when a BinanceAPIException Exception is raised"""
        from utils.mail_helper import MailHelper
        MailHelper.send_exception_mail(error.message)
        return {
            "message": error.message,
            "code": error.code
        }, getattr(error, 'status_code', 500)

    @app.errorhandler(404)
    def page_not_found(error):
        return {}, 404

    @app.errorhandler(Exception)
    def internal_sever_error(error):
        from tasks import send_exception_mail

        logger.exception(
            f'Error Occured Processing Incoming AI Data',
            exc_info=error)

        if hasattr(error, 'message'):
            send_exception_mail.delay(error.message)
        else:
            send_exception_mail.delay(
                'Error Occured Processing Incoming AI Data')

        return {
            "message": "Error Occured Processing Incoming AI Data",
        }, 500

    @app.route("/")
    def hello_world():
        return "<h1>Hello Carina, what do you want to do today?</h1>"

    return app
