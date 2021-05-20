# Model to log all incoming coins and their current
# CoinsStatusModel - id, created_at, updated_at, coin_name, trigger_one_status, trigger_two_status

from uuid import uuid4

from main import db
from sqlalchemy import func
from utils.model_utils import UtilityMixin


class IncomingCoinLog(UtilityMixin, db.Model):  # type: ignore
    """ Logging Model that stores all incoming data from AI Server """

    id = db.Column(db.Integer, primary_key=True)
    recieved_at = db.Column(db.DateTime, server_default=func.now())
    coin_name = db.Column(db.String(100), nullable=False)
    incoming_trigger = db.Column(db.String(10), nullable=False)
    trigger_status = db.Column(db.Boolean, nullable=False)


class CoinState(UtilityMixin, db.Model):  # type: ignore
    """ User model for storing user related information """

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now())
    coin_name = db.Column(db.String(100), unique=True, nullable=False)
    trigger_one_status = db.Column(db.Boolean, default=False, nullable=False)
    trigger_two_status = db.Column(db.Boolean, default=False, nullable=False)
