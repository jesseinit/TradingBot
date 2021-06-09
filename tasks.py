from datetime import datetime
from typing import Literal
from decouple import config
from utils.wallet_helper import Wallet
from main import celery, logger
from utils.mail_helper import MailHelper

ALLOWED_MAILS = config(
    'MAIL_ADDRS',
    cast=lambda emails: [email.strip() for email in emails.split(',')])


@celery.task(bind=True, name='task.check_order_status')
def check_order_status(self, mode: Literal['12h', '5m'] = None, symbol: str = None, order_id: str = None):
    """ This task runs a check to see if a buy order has been filled or not """
    logger.info("Running Background Job to Check Order Status >>>")
    try:
        order_details = Wallet.retrive_order_details(symbol, order_id)
        if order_details and order_details['status'] != "FILLED":
            Wallet.cancel_order(symbol, order_id)
            logger.info("Check Completed and Order Cancelled >>>")
            return 'Order Cancelled'

        if order_details and order_details['status'] == "FILLED":
            # Todo - Get Coin and set is_holding to true
            from blueprints.listener.listener_models import CoinState, FiveMinsCoinState
            from blueprints.wallet.wallet_models import TransactionsAudit
            coin_name = symbol.split("USDT")[0]
            if mode == '12h':
                coin_instance = CoinState.query.filter_by(
                    coin_name=coin_name).first()
                if coin_instance:
                    coin_instance.update(is_holding=True)
            elif mode == '5m':
                coin_instance = FiveMinsCoinState.query.filter_by(
                    coin_name=coin_name).first()
                if coin_instance:
                    coin_instance.update(is_holding=True)

            TransactionsAudit(
                occured_at=datetime .fromtimestamp(
                    int(str(order_details['time'])[:10])),
                symbol=order_details['symbol'],
                client_order_id=order_details['orderId'],
                orig_qty=order_details['origQty'],
                executed_qty=order_details['executedQty'],
                cummulative_quote_qty=order_details[
                    'cummulativeQuoteQty'],
                order_status=order_details['status'],
                time_in_force=order_details['timeInForce'],
                order_type=order_details['type'],
                side=order_details['side'],
                fills=[]).save()
            logger.info("Check Completed and Order Filled >>>")
            return 'Order Filled'
    except Exception as e:
        raise self.retry(exc=e, countdown=1, max_retries=3)


@celery.task(bind=True, name='mail.send_ai_incoming_mail')
def send_ai_incoming_mail(self, *args, **kwargs):
    try:
        return MailHelper.send_ai_incoming_mail(*args, **kwargs)
    except Exception as e:
        raise self.retry(exc=e, countdown=1, max_retries=1)


@celery.task(name='mail.send_success_buy_mail')
def send_success_buy_mail(*args, **kwargs):
    return MailHelper.send_success_buy_mail(*args, **kwargs)


@celery.task(name='mail.send_success_sell_mail')
def send_success_sell_mail(*args, **kwargs):
    return MailHelper.send_success_sell_mail(*args, **kwargs)


@celery.task(name='mail.send_cancel_mail')
def send_cancel_mail(*args, **kwargs):
    return MailHelper.send_cancel_mail(*args, **kwargs)


@celery.task(name='mail.send_exception_mail')
def send_exception_mail(*args, **kwargs):
    return MailHelper.send_exception_mail(*args, **kwargs)
