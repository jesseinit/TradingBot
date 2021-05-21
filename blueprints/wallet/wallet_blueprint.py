from flask import Blueprint
from utils.wallet_helper import BinanceClient, Wallet

wallet_blueprint = Blueprint(
    "wallet_blueprint", __name__, url_prefix="/api/v1/wallet"
)


@wallet_blueprint.route("/balance")
def get_wallet_balance():
    # all_coins_data = Wallet.retrieve_coins_balance()
    # if all_coins_data is None:
    #     return {"error": "Cannot access Balance"}, 400

    # coins_balances = [
    #     dict(coin=coin['coin'], name=coin['name'], free=coin['free'],
    #          locked=coin['locked'], freeze=coin['freeze'])
    #     for coin in all_coins_data if coin['coin'] in Wallet.WALLET_COINS]

    # return {"data": coins_balances}

    coins_balances = [
        BinanceClient.get_asset_balance(asset=coin)
        for coin in Wallet.WALLET_COINS]

    return {"data": coins_balances}
