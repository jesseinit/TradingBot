from main import db
from sqlalchemy import func
from utils.model_utils import UtilityMixin
from utils.wallet_helper import Wallet


class IncomingCoinLog(UtilityMixin, db.Model):  # type: ignore
    """ Logging Model that stores all incoming data from AI Server """

    id = db.Column(db.Integer, primary_key=True)
    received_at = db.Column(db.DateTime, server_default=func.now())
    coin_name = db.Column(db.String(100), nullable=False)
    t1 = db.Column(db.Boolean, nullable=True)
    t2 = db.Column(db.Boolean, nullable=True)
    t3 = db.Column(db.Boolean, nullable=True)
    t4 = db.Column(db.Boolean, nullable=True)
    price = db.Column(db.Float, nullable=True)


class CoinState(UtilityMixin, db.Model):  # type: ignore
    """ 5min Table """

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now())
    coin_name = db.Column(db.String(100), unique=True, nullable=False)
    trigger_one_status = db.Column(db.Boolean, default=None, nullable=True)
    trigger_two_status = db.Column(db.Boolean, default=None, nullable=True)
    trigger_three_status = db.Column(db.Boolean, default=None, nullable=True)
    trigger_four_status = db.Column(db.Boolean, default=None, nullable=True)
    is_holding = db.Column(db.Boolean, index=True,
                           default=False, nullable=True)

    def compute_trigger_state(self):
        # ? We buy when any of the triggers is true for the valid coins and we are not holding the coin
        if self.coin_name in Wallet.VALID_COINS_12H and any([
                self.trigger_one_status, self.trigger_two_status,
                self.trigger_three_status, self.trigger_four_status]) and self.is_holding is False:
            return "BUY"

        if self.coin_name in Wallet.VALID_COINS_12H and all([
                self.trigger_one_status is False,
                self.trigger_two_status is False,
                self.trigger_three_status is False,
                self.trigger_four_status is False]) and self.is_holding is True:
            return "SELL"


class FiveMinsCoinState(UtilityMixin, db.Model):  # type: ignore
    """ 5min Table """

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now())
    coin_name = db.Column(db.String(100), unique=True, nullable=False)
    trigger_one_status = db.Column(db.Boolean, default=None, nullable=True)
    trigger_two_status = db.Column(db.Boolean, default=None, nullable=True)
    is_holding = db.Column(db.Boolean, index=True,
                           default=False, nullable=True)

    def compute_trigger_state(self):
        if self.coin_name in Wallet.VALID_COINS_5M and all([self.trigger_one_status is True, self.trigger_two_status is True, self.is_holding is False]):
            return "BUY"

        if self.coin_name in Wallet.VALID_COINS_5M and self.trigger_one_status is False and self.trigger_two_status is True and self.is_holding is True:
            return "SELL"

        if self.coin_name in Wallet.VALID_COINS_5M and self.trigger_one_status is True and self.trigger_two_status is False and self.is_holding is True:
            return "SELL"

        if self.coin_name in Wallet.VALID_COINS_5M and all([self.trigger_one_status is False or self.trigger_two_status is False]) and self.is_holding is True:
            return "SELL"
