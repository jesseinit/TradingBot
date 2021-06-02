# Model to log all incoming coins and their current
# CoinsStatusModel - id, created_at, updated_at, coin_name, trigger_one_status, trigger_two_status

from typing import Literal, Union
from utils.wallet_helper import Wallet
from main import db
from sqlalchemy import func
from utils.model_utils import UtilityMixin


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
    # trigger_status = db.Column(db.Boolean, nullable=False)


class CoinState(UtilityMixin, db.Model):  # type: ignore
    """ User model for storing user related information """

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

    def compute_trigger_state(self, chart_mode: Literal['twelve_hrs_chart', "five_mins_chart"] = 'twelve_hrs_chart'):
        # ? We buy when any of the triggers is true for the valid coins and we are not holding the coin
        if chart_mode == "twelve_hrs_chart":
            if self.coin_name in Wallet.VALID_COINS and any([
                    self.trigger_one_status, self.trigger_two_status,
                    self.trigger_three_status, self.trigger_four_status]) and self.is_holding is False:
                return "BUY"

            # ? We return this when all of the triggers turns false and we are currently holding it
            if self.coin_name in Wallet.VALID_COINS and all([
                    self.trigger_one_status is False,
                    self.trigger_two_status is False,
                    self.trigger_three_status is False,
                    self.trigger_four_status is False]) and self.is_holding is True:
                return "SELL"

        # ? Use this for the previous logic(5mins timeline)
        # if chart_mode == "five_mins_chart":
        #     if self.coin_name in Wallet.VALID_COINS and all([self.trigger_one_status is True, self.trigger_two_status is True, self.is_holding is False]):
        #         return "BUY"

        #     if self.coin_name in Wallet.VALID_COINS and self.trigger_one_status is False and self.trigger_two_status is True and self.is_holding is True:
        #         return "SELL"

        #     if self.coin_name in Wallet.VALID_COINS and self.trigger_one_status is True and self.trigger_two_status is False and self.is_holding is True:
        #         return "SELL"

        #     if self.coin_name in Wallet.VALID_COINS and all([self.trigger_one_status is False or self.trigger_two_status is False]) and self.is_holding is True:
        #         return "SELL"

    @classmethod
    def currently_held_coins(cls):
        """ Returns the number of coins we are currently holding(Already bought and waiting to sell) """
        currently_holding = cls.query.filter_by(is_holding=True).all()
        return 0 if currently_holding is None else len(currently_holding)

    def __str__(self) -> str:
        return f"<CoinState {self.coin_name}, T1={self.trigger_one_status}, T2={self.trigger_two_status} is_holding={self.is_holding}>"

    def __repr__(self) -> str:
        return f"<CoinState {self.coin_name}, T1={self.trigger_one_status}, T2={self.trigger_two_status} is_holding={self.is_holding}>"
