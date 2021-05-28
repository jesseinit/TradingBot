
import json
from datetime import datetime

from blueprints.listener.listener_models import CoinState, IncomingCoinLog
from blueprints.wallet.wallet_models import TransactionsAudit
from flask import Blueprint, request
from utils.mail_helper import MailHelper
from utils.wallet_helper import Wallet
from main import logger

listener_blueprint = Blueprint(
    "listener_blueprint", __name__, url_prefix="/api/v1/listener"
)


@listener_blueprint.route("/webhook", methods=["POST"])
def ai_listener():
    try:
        ai_response = request.get_json(force=True)
        coin_signal = ai_response.get('data')[0]
        coin_name, trigger_name, price = coin_signal.keys()
        recieved_at = datetime.now()

        incoming_log_instance = IncomingCoinLog(
            received_at=recieved_at, coin_name=coin_signal[coin_name],
            incoming_trigger=trigger_name, trigger_status=True if coin_signal[trigger_name] == "TRUE" else False)
        incoming_log_instance.save()

        # Create/Update Coin State Record
        coin_instance = CoinState.query.filter_by(
            coin_name=coin_signal[coin_name]).first()

        signal_type = {
            "trigger1": True if trigger_name == "trigger1" and coin_signal[
                trigger_name] == "TRUE" else False,
            "trigger2": True if trigger_name == "trigger2" and coin_signal[
                trigger_name] == "TRUE" else False
        }

        logger.info(
            f'INCOMING AI DATA>>> COIN_NAME:{coin_signal[coin_name]} SIGNAL:{trigger_name} VALUE:{signal_type[trigger_name]}')

        if not coin_instance:
            # Create the coin record for the first time
            CoinState(coin_name=coin_signal[coin_name],
                      trigger_one_status=signal_type['trigger1'],
                      trigger_two_status=signal_type["trigger2"]).save()
            MailHelper.send_ai_incoming_mail(
                recieved_at=recieved_at, coin_name=coin_signal[coin_name],
                trigger_name=trigger_name, trigger_value=signal_type[trigger_name])
            return {"status": "response recieved"}

        # Update only coins we are not currently holding.
        if trigger_name == "trigger1":
            coin_instance.update(
                trigger_one_status=signal_type['trigger1'],
                updated_at=datetime.now())

        if trigger_name == "trigger2":
            coin_instance.update(
                trigger_two_status=signal_type['trigger2'],
                updated_at=datetime.now())

        # Check current coin state
        coin_state_instance = CoinState.query.filter_by(
            coin_name=coin_signal[coin_name]).first()

        # Compute coin trigger state
        trigger_state = coin_state_instance.compute_trigger_state()
        currently_held_coin = CoinState.currently_held_coin()

        order_data = None
        # We buy only when we are not holding any coin.
        if trigger_state == "BUY" and currently_held_coin is None:
            buy_order_details = Wallet.buy_order(
                symbol=f"{coin_state_instance.coin_name.upper()}USDT")
            if buy_order_details:
                order_data = buy_order_details
                coin_state_instance.update(is_holding=True)
                with open("buy_orders.log", 'a') as buy_log:
                    buy_log.write(f"{json.dumps(buy_order_details)}\n\n")
                TransactionsAudit(
                    occured_at=datetime.fromtimestamp(
                        int(str(buy_order_details['transactTime'])[:10])),
                    symbol=buy_order_details['symbol'],
                    client_order_id=buy_order_details['clientOrderId'],
                    orig_qty=buy_order_details['origQty'],
                    executed_qty=buy_order_details['executedQty'],
                    cummulative_quote_qty=buy_order_details['cummulativeQuoteQty'],
                    order_status=buy_order_details['status'],
                    time_in_force=buy_order_details['timeInForce'],
                    order_type=buy_order_details['type'],
                    side=buy_order_details['side'],
                    fills=buy_order_details['fills']
                ).save()
                MailHelper.send_ai_incoming_mail(
                    recieved_at=recieved_at, coin_name=coin_signal[coin_name],
                    trigger_name=trigger_name, trigger_value=signal_type[trigger_name])
                MailHelper.send_success_buy_mail(
                    order_details=buy_order_details)
                return {"status": "response recieved", "data": order_data['fills'] if order_data else None}

        if trigger_state == "SELL":

            sell_order_details = Wallet.sell_order(
                symbol=f"{coin_state_instance.coin_name.upper()}USDT")
            if sell_order_details:
                order_data = sell_order_details
                coin_state_instance.update(
                    is_holding=False)
                with open("sell_orders.log", 'a') as sell_log:
                    sell_log.write(f"{json.dumps(sell_order_details)}\n\n")
                TransactionsAudit(
                    occured_at=datetime.fromtimestamp(
                        int(str(sell_order_details['transactTime'])[:10])),
                    symbol=sell_order_details['symbol'],
                    client_order_id=sell_order_details['clientOrderId'],
                    orig_qty=sell_order_details['origQty'],
                    executed_qty=sell_order_details['executedQty'],
                    cummulative_quote_qty=sell_order_details['cummulativeQuoteQty'],
                    order_status=sell_order_details['status'],
                    time_in_force=sell_order_details['timeInForce'],
                    order_type=sell_order_details['type'],
                    side=sell_order_details['side'],
                    fills=sell_order_details['fills']
                ).save()
                MailHelper.send_ai_incoming_mail(
                    recieved_at=recieved_at, coin_name=coin_signal[coin_name],
                    trigger_name=trigger_name, trigger_value=signal_type[trigger_name])
                MailHelper.send_success_sell_mail(
                    order_details=sell_order_details)
                return {"status": "response recieved", "data": order_data['fills'] if order_data else None}

            MailHelper.send_ai_incoming_mail(
                recieved_at=recieved_at, coin_name=coin_signal[coin_name],
                trigger_name=trigger_name, trigger_value=signal_type[trigger_name])

            return {"status": "response recieved", "data": order_data['fills'] if order_data else None}
    except Exception as e:
        logger.exception(
            f'Error Occured Processing Incoming AI Data', exc_info=e)

    return {"status": "response recieved"}
