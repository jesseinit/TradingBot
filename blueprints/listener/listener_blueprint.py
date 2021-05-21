
from utils.wallet_helper import BinanceClient, Wallet
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

    # Coin Record Exists So we update trigger state
    if trigger_name == "trigger1" and coin_instance.is_holding is False:
        coin_instance.update(
            trigger_one_status=signal_type['trigger1'])

    if trigger_name == "trigger2" and coin_instance.is_holding is False:
        coin_instance.update(
            trigger_two_status=signal_type['trigger2'])

    # Check currentl coin state
    coin_state_instance = CoinState.query.filter_by(
        coin_name=coin_signal[coin_name]).first()

    # Compute coin trigger state
    trigger_state = coin_state_instance.compute_trigger_state()

    print("trigger_state>>>>", trigger_state)

    # Gets coin balance date for USDT
    base_coin_balance_data = Wallet.retrieve_coin_balance()

    # Parse avialable balance of USDT to float
    free_coin_bal = float(base_coin_balance_data.get('free', 0.0))

    if trigger_state == "BUY" and free_coin_bal > 10:
        # compute 99.8% of coin
        # buy coin with usdt
        order = Wallet.create_test_order(
            symbol=f"{coin_state_instance.coin_name}USDT")

        print("ORDERRR>>>", order)
        # TODO - Create TransactionOrder table to record logs
        # set the coin to HOLD by updating is_holding field to true
        # set update the trigger_one_status and trigger_two_status to null as a reset mechanism
        coin_state_instance.update(
            is_holding=True, trigger_one_status=None, trigger_two_status=None)

        print(f"BOUGHT {coin_state_instance.coin_name} with USDT")

    if trigger_state == "SELL" and free_coin_bal > 10:
        # Todo - Complete
        # We can only sell a coin if we are currently holding it

        # Trigger a buy order
        coin_state_instance.update(
            is_holding=False, trigger_one_status=None, trigger_two_status=None)

        print(f"BOUGHT {coin_state_instance.coin_name} with USDT")

    # print("base_coin_balance>>>", float(base_coin_balance_data['free']))
    # Todo - Implement the required wallet methods to wther sell or buy coins.

    return {"status": "response recieved"}
