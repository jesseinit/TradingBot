import os

from decouple import config


class Config:
    SQLALCHEMY_ECHO = True
    SECRET_KEY = config("SECRET_KEY")
    MAIL_SERVER = 'smtp.office365.com'
    MAIL_PORT = 587
    MAIL_USERNAME = "alerts@chc.capital"
    MAIL_PASSWORD = config("SMTP_PASSWORD_ALERTS")
    MAIL_DEFAULT_SENDER = ("TrdBot Alerts", "alerts@chc.capital")
    MAIL_USE_SSL = False
    MAIL_USE_TLS = True
    MAIL_DEBUG = False
    # SQLALCHEMY_ENGINE_OPTIONS = {
    #     "pool_pre_ping": True,
    #     "pool_recycle": 300,
    # }


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = config("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = config("DATABASE_URL")
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = config("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True


config = dict(development=DevelopmentConfig,
              test=TestingConfig,
              production=ProductionConfig)
