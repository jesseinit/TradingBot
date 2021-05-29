from tasks import greet
from flask import Blueprint
from utils.wallet_helper import Wallet
from main import logger

wallet_blueprint = Blueprint("wallet_blueprint",
                             __name__,
                             url_prefix="/api/v1/wallet")


@wallet_blueprint.route("/balance")
def get_wallet_balance():
    logger.info(f'RETRIEVING BALANCE FOR ALL SYMBOLS')
    greet.apply_async(countdown=3)
    coins_balances = [
        Wallet.retrieve_coin_balance(coin=coin) for coin in Wallet.WALLET_COINS
    ]
    logger.info(f'RETRIEVED BALANCE FOR ALL SYMBOLS')
    return {"data": coins_balances}
