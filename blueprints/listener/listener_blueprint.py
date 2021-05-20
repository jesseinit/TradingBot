
from sqlalchemy.sql.expression import update
from blueprints.listener.listener_models import IncomingCoinLog, CoinState
from flask import Blueprint, request
from datetime import datetime
listener_blueprint = Blueprint(
    "listener_blueprint", __name__, url_prefix="/api/v1/listener"
)


@listener_blueprint.route("/webhook", methods=["POST"])
def ai_listener():
    # Track Trigger1 and Trigger2 for all coins in Wallet.TRADING_COINS
    # When Trigger1 and Trigger2 turns TRUE for a specific coin AND we have a balance in USDT(i.e we are not holding any coin) then we buy said coin with USDT
    # When Trigger1 and Trigger2 turns FALSE for a specific coin that has been bought, we swap said coin to USDT

    # We only swap coin to USDT when the both Trigeer 1 and 2 turns false on the coins we are holding.
    # We need to know if we are holding a coin and what coin is help

    # Creates a log of the incoming AI signal
    ai_response = request.get_json(force=True)
    coin_signal = ai_response.get('data')[0]
    coin_name, trigger_name = coin_signal.keys()
    recieved_at = datetime.now()
    incoming_log_instance = IncomingCoinLog(received_at=recieved_at, coin_name=coin_signal[coin_name],
                                            incoming_trigger=trigger_name,
                                            trigger_status=True if coin_signal[trigger_name] == "TRUE" else False)
    incoming_log_instance.save()

    # Create/Update Coin State Record
    existing_user_instance = CoinState.query.filter_by(
        coin_name=coin_signal[coin_name]).first()

    signal_type = {
        "trigger1": True if trigger_name == "trigger1" and coin_signal[
            trigger_name] == "TRUE" else False,
        "trigger2": True if trigger_name == "trigger2" and coin_signal[
            trigger_name] == "TRUE" else False
    }

    if not existing_user_instance:
        # Create the coin record for the first time
        CoinState(coin_name=coin_signal[coin_name],
                  trigger_one_status=signal_type['trigger1'],
                  trigger_two_status=signal_type["trigger2"]).save()
        return {"status": "response recieved"}

    # Coin Record Exists So we update
    if trigger_name == "trigger1":
        existing_user_instance.update(
            trigger_one_status=signal_type['trigger1'])

    if trigger_name == "trigger2":
        existing_user_instance.update(
            trigger_two_status=signal_type['trigger2'])

    # Todo - We check for the trigger state of the coin to either swap coin to usdt(sell) or to swap to another coin with usdt(buy)
    updated_coin_instance = CoinState.query.filter_by(
        coin_name=coin_signal[coin_name]).first()

    # Todo - Implement the required wallet methods to wther sell or buy coins.

    return {"status": "response recieved"}
