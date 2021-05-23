from flask import Blueprint
from utils.wallet_helper import BinanceClient, Wallet

wallet_blueprint = Blueprint(
    "wallet_blueprint", __name__, url_prefix="/api/v1/wallet"
)


@wallet_blueprint.route("/balance")
def get_wallet_balance():
    coins_balances = [
        BinanceClient.get_asset_balance(asset=coin)
        for coin in Wallet.WALLET_COINS]

    return {"data": coins_balances}
