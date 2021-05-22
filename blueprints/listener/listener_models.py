# Model to log all incoming coins and their current
# CoinsStatusModel - id, created_at, updated_at, coin_name, trigger_one_status, trigger_two_status

from main import db
from sqlalchemy import func
from utils.model_utils import UtilityMixin


class IncomingCoinLog(UtilityMixin, db.Model):  # type: ignore
    """ Logging Model that stores all incoming data from AI Server """

    id = db.Column(db.Integer, primary_key=True)
    received_at = db.Column(db.DateTime, server_default=func.now())
    coin_name = db.Column(db.String(100), nullable=False)
    incoming_trigger = db.Column(db.String(10), nullable=False)
    trigger_status = db.Column(db.Boolean, nullable=False)


class CoinState(UtilityMixin, db.Model):  # type: ignore
    """ User model for storing user related information """

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now())
    coin_name = db.Column(db.String(100), unique=True, nullable=False)
    trigger_one_status = db.Column(db.Boolean, default=False, nullable=True)
    trigger_two_status = db.Column(db.Boolean, default=False, nullable=True)
    is_holding = db.Column(db.Boolean, index=True,
                           default=False, nullable=True)

    def compute_trigger_state(self):
        # Swap USDT to COIN
        if all([self.trigger_one_status is True, self.trigger_two_status is True, self.is_holding is False]):
            return "BUY"

        # Swap COIN to USDT
        # We return this when both triggers are false and we are currently holding it
        if all([self.trigger_one_status is False, self.trigger_two_status is False, self.is_holding is True]):
            return "SELL"

        return None

    @classmethod
    def currently_held_coin(cls):
        """ Returns the coin we are currently holding(Already bought and waiting to sell) """
        currently_holding = cls.query.filter_by(
            is_holding=True).first()
        return currently_holding

    def __str__(self) -> str:
        return f"<CoinState {self.coin_name}, T1={self.trigger_one_status}, T2={self.trigger_two_status} is_holding={self.is_holding}>"

    def __repr__(self) -> str:
        return f"<CoinState {self.coin_name}, T1={self.trigger_one_status}, T2={self.trigger_two_status} is_holding={self.is_holding}>"


# class TradeTransactions(UtilityMixin, db.Model):  # type: ignore
#     """ Model to log all market trades """

#     id = db.Column(db.Integer, primary_key=True)
#     created_at = db.Column(db.DateTime, server_default=func.now())
#     symbol = db.Column(db.String(10), nullable=False)
#     order_id = db.Column(db.Integer, nullable=False)
