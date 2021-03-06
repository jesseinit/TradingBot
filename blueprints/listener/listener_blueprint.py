import json
from datetime import datetime

from blueprints.listener.listener_models import CoinState as TwelveHrsCoinState
from blueprints.listener.listener_models import (FiveMinsCoinState,
                                                 IncomingCoinLog)
from blueprints.listener.listener_serializer import AIDataSchema
from blueprints.wallet.wallet_models import TransactionsAudit
from flask import Blueprint, request
from main import logger
from tasks import (send_ai_incoming_mail, send_success_buy_mail,
                   send_success_sell_mail)
from utils.mail_helper import MailHelper
from utils.wallet_helper import Wallet

listener_blueprint = Blueprint("listener_blueprint",
                               __name__,
                               url_prefix="/api/v1/listener")


@listener_blueprint.route("/webhook", methods=["POST"])
def ai_listener():
    try:
        ai_response = request.get_json(force=True)
        coin_signal = ai_response.get('data')[0]
        logger.info(f'INCOMING AI DATA>>>>{json.dumps(ai_response)}')

        coin_signal = AIDataSchema().load(coin_signal)

        recieved_at = datetime.now()

        incoming_log_instance = IncomingCoinLog(
            received_at=recieved_at,
            coin_name=coin_signal.get('coin'),
            t1=coin_signal.get('trigger1'),
            t2=coin_signal.get('trigger2'),
            t3=coin_signal.get('trigger3'),
            t4=coin_signal.get('trigger4'),
            price=coin_signal.get('price')
        )
        incoming_log_instance.save()

        trigger_mode = coin_signal.get("time")

        if trigger_mode == '5m':
            coin_instance = FiveMinsCoinState.query.filter_by(
                coin_name=coin_signal.get('coin')).first()
            if not coin_instance:
                FiveMinsCoinState(
                    coin_name=coin_signal.get('coin'),
                    trigger_one_status=coin_signal.get('trigger1'),
                    trigger_two_status=coin_signal.get('trigger2'),
                    updated_at=datetime.now()
                ).save()

        coin_state_instance = FiveMinsCoinState.query.filter_by(
            coin_name=coin_signal.get('coin')).first()

        # Compute coin trigger state
        trigger_state = coin_state_instance.compute_trigger_state(
            incoming_t1_value=coin_signal.get('trigger1'),
            incoming_t2_value=coin_signal.get('trigger2'))

        logger.info(
            f'Trigger State for {coin_signal.get("coin")} == {trigger_state}')

        # return {"status": "response recieved", "data": coin_signal}

        if trigger_state == "BUY":
            send_ai_incoming_mail.delay(
                recieved_at=recieved_at, coin_name=coin_signal.get('coin'),
                details=json.dumps(coin_signal))
            buy_order_details = Wallet.buy_limit_order(
                symbol=f"{coin_state_instance.coin_name.upper()}USDT",
                price=coin_signal['price'], mode=trigger_mode)

            if buy_order_details:
                # ? Persis state change to DB
                coin_state_instance.update(
                    trigger_one_status=coin_signal.get(
                        'trigger1', coin_state_instance.trigger_one_status),
                    trigger_two_status=coin_signal.get(
                        'trigger2', coin_state_instance.trigger_two_status),
                    updated_at=datetime.now())

                # ? We hav to ensure that some orders in buy_order_details have status filled before we set coin to a holding state
                has_filled_orders = bool(
                    list(filter(lambda order: order['status'] == 'FILLED', buy_order_details)))
                if has_filled_orders:
                    coin_state_instance.update(is_holding=True)

                for order_detail in buy_order_details:
                    if has_filled_orders:
                        with open("logs/buy_orders.log", 'a') as buy_log:
                            buy_log.write(f"{json.dumps(order_detail)}\n\n")
                        TransactionsAudit(
                            occured_at=datetime.fromtimestamp(
                                int(str(order_detail['transactTime'])[:10])),
                            symbol=order_detail['symbol'],
                            client_order_id=order_detail['orderId'],
                            orig_qty=order_detail['origQty'],
                            executed_qty=order_detail['executedQty'],
                            cummulative_quote_qty=order_detail[
                                'cummulativeQuoteQty'],
                            order_status=order_detail['status'],
                            time_in_force=order_detail['timeInForce'],
                            order_type=order_detail['type'],
                            side=order_detail['side'],
                            fills=order_detail['fills']).save()
                return {"status": "response recieved", "data": buy_order_details}
            return {"status": "response recieved"}

        if trigger_state == "SELL":
            sell_order_details = Wallet.sell_order(
                symbol=f"{coin_state_instance.coin_name.upper()}USDT")
            if sell_order_details:
                # ? Persis state change to DB
                coin_state_instance.update(
                    trigger_one_status=coin_signal.get(
                        'trigger1', coin_state_instance.trigger_one_status),
                    trigger_two_status=coin_signal.get(
                        'trigger2', coin_state_instance.trigger_two_status),
                    updated_at=datetime.now(),
                    is_holding=False)

                with open("logs/sell_orders.log", 'a') as sell_log:
                    sell_log.write(f"{json.dumps(sell_order_details)}\n\n")

                TransactionsAudit(
                    occured_at=datetime.fromtimestamp(
                        int(str(sell_order_details['transactTime'])[:10])),
                    symbol=sell_order_details['symbol'],
                    client_order_id=sell_order_details['orderId'],
                    orig_qty=sell_order_details['origQty'],
                    executed_qty=sell_order_details['executedQty'],
                    cummulative_quote_qty=sell_order_details[
                        'cummulativeQuoteQty'],
                    order_status=sell_order_details['status'],
                    time_in_force=sell_order_details['timeInForce'],
                    order_type=sell_order_details['type'],
                    side=sell_order_details['side'],
                    fills=sell_order_details['fills']).save()

                send_ai_incoming_mail.delay(
                    recieved_at=recieved_at, coin_name=coin_signal.get('coin'),
                    details=json.dumps(coin_signal))
                send_success_sell_mail.delay(order_details=sell_order_details)

                return {
                    "status": "response recieved",
                    "data": sell_order_details['fills'] if sell_order_details else None
                }

            return {"status": "response recieved and rolled"}

    except Exception as e:
        ai_response = request.get_json(force=True)
        logger.exception(
            f'Error Occured Processing Incoming AI Data',
            exc_info=e,
            extra={"custom_dimensions": {
                "ai_data": json.dumps(ai_response)
            }})

    return {"status": "response recieved"}
