from main import db, logger
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

    def compute_trigger_state(self, incoming_t1_value=None, incoming_t2_value=None):
        current_t1_value = self.trigger_one_status
        current_t2_value = self.trigger_two_status

        if incoming_t1_value is not None:
            final_t1_value = incoming_t1_value
        else:
            final_t1_value = current_t1_value

        if incoming_t2_value is not None:
            final_t2_value = incoming_t2_value
        else:
            final_t2_value = current_t2_value

        if self.coin_name in Wallet.VALID_COINS_5M and all([final_t1_value is True, final_t2_value is True, self.is_holding is False]):
            return "BUY"

        if self.coin_name in Wallet.VALID_COINS_5M and final_t1_value is False and final_t2_value is True and self.is_holding is True:
            return "SELL"

        if self.coin_name in Wallet.VALID_COINS_5M and final_t1_value is True and final_t2_value is False and self.is_holding is True:
            return "SELL"

        if self.coin_name in Wallet.VALID_COINS_5M and all([final_t1_value is False or final_t2_value is False]) and self.is_holding is True:
            return "SELL"
