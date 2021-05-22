
from datetime import datetime
import json

from sqlalchemy.sql.expression import false

from blueprints.listener.listener_models import CoinState, IncomingCoinLog
from flask import Blueprint, request
from utils.wallet_helper import BinanceClient, Wallet

listener_blueprint = Blueprint(
    "listener_blueprint", __name__, url_prefix="/api/v1/listener"
)


@listener_blueprint.route("/webhook", methods=["POST"])
def ai_listener():
    ai_response = request.get_json(force=True)
    coin_signal = ai_response.get('data')[0]
    coin_name, trigger_name = coin_signal.keys()
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

    if not coin_instance:
        # Create the coin record for the first time
        CoinState(coin_name=coin_signal[coin_name],
                  trigger_one_status=signal_type['trigger1'],
                  trigger_two_status=signal_type["trigger2"]).save()
        return {"status": "response recieved"}

    # Update only coins we are not currently holding.
    if trigger_name == "trigger1":
        coin_instance.update(
            trigger_one_status=signal_type['trigger1'])

    if trigger_name == "trigger2":
        coin_instance.update(
            trigger_two_status=signal_type['trigger2'])

    # Check current coin state
    coin_state_instance = CoinState.query.filter_by(
        coin_name=coin_signal[coin_name]).first()

    # Compute coin trigger state
    trigger_state = coin_state_instance.compute_trigger_state()
    currently_held_coin = CoinState.currently_held_coin()

    # We buy only when we are not holding any coin.
    if trigger_state == "BUY" and currently_held_coin is None:
        order = Wallet.buy_order(
            symbol=f"{coin_state_instance.coin_name.upper()}USDT")
        coin_state_instance.update(is_holding=True)
        with open("buy_orders.log", 'a') as buy_log:
            buy_log.write(f"{json.dumps(order)}\n")

    if trigger_state == "SELL":
        sell_order_details = Wallet.sell_order(
            symbol=f"{coin_state_instance.coin_name.upper()}USDT")
        coin_state_instance.update(
            is_holding=False)
        with open("sell_orders.log", 'a') as sell_log:
            sell_log.write(f"{json.dumps(sell_order_details)}\n")

    return {"status": "response recieved"}
