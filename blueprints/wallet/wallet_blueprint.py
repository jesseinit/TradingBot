from flask import Blueprint
from utils.binance.wallet import Wallet

wallet_blueprint = Blueprint(
    "wallet_blueprint", __name__, url_prefix="/api/v1/wallet"
)


@wallet_blueprint.route("/balance")
def get_wallet_balance():
    all_coins_data = Wallet.retrieve_coins_balance()
    coins_balances = [
        dict(coin=coin['coin'], name=coin['name'], free=coin['free'],
             locked=coin['locked'], freeze=coin['freeze'])
        for coin in all_coins_data if coin['coin'] in Wallet.REQUIRED_COINS]
    return {"data": coins_balances}
