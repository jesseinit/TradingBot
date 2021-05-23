from main import db
from sqlalchemy import func
from utils.model_utils import UtilityMixin


class TransactionsAudit(UtilityMixin, db.Model):
    """ Model to log all market trades """

    id = db.Column(db.Integer, primary_key=True)
    occured_at = db.Column(db.DateTime, default=func.now())
    symbol = db.Column(db.String(10), nullable=False)
    client_order_id = db.Column(db.String(100), nullable=False)
    orig_qty = db.Column(db.Float, nullable=False)
    executed_qty = db.Column(db.Float, nullable=False)
    cummulative_quote_qty = db.Column(db.Float, nullable=False)
    order_status = db.Column(db.String(50), nullable=False)
    time_in_force = db.Column(db.String(10), nullable=False)
    order_type = db.Column(db.String(20), nullable=False)
    side = db.Column(db.String(10), nullable=False)
    # price = db.Column(db.Float, nullable=False)
    # commission = db.Column(db.Float, nullable=False)
    # commission_asset = db.Column(db.String(10), nullable=False)
    # trade_id = db.Column(db.Integer, nullable=False)
    fills = db.Column(db.JSON, nullable=False)
