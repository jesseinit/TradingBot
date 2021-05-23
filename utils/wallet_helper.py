import hashlib
import hmac
import time

import requests
from binance.client import Client
from binance.enums import ORDER_TYPE_MARKET, SIDE_BUY, SIDE_SELL
from decouple import config

CURRENT_ENV = config('FLASK_ENV')


BINANCE_API_KEY = config("BINANCE_API_KEY")
BINANCE_API_SECRET = config("BINANCE_API_SECRET")

BinanceClient = Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)


class Wallet:
    """ Manages all operations to be performed on a binance wallet """

    BINANCE_API_KEY = config("BINANCE_API_KEY")
    BINANCE_API_SECRET = config("BINANCE_API_SECRET")
    BINANCE_BASE_URL = "https://api1.binance.com"
    WALLET_COINS = ["BTC", "USDT", "ETH", "XLM", "LINK", "ADA", "ETC"]
    TRADING_COINS = ["BTC", "ETH", "XLM", "LINK", "ADA", "ETC"]

    @classmethod
    def get_timestamp(cls):
        return int(time.time() * 1000)

    @classmethod
    def get_signature(cls, query_string):
        return hmac.new(cls.BINANCE_API_SECRET.encode(
            'utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    @classmethod
    def retrieve_coins_balance(cls):
        """ Gets all coins balances of a wallet """
        timestamp = cls.get_timestamp()
        query_string = f"timestamp={timestamp}"
        signature = cls.get_signature(query_string)
        response = requests.get(
            f"{cls.BINANCE_BASE_URL}/sapi/v1/capital/config/getall",
            params={"timestamp": timestamp, "signature": signature},
            headers={
                "X-MBX-APIKEY": cls.BINANCE_API_KEY
            }
        )

        if not response.ok:
            print(response.text)
            return None

        return response.json()

    @classmethod
    def retrieve_coin_balance(cls, coin: str = "USDTTT"):
        """ Gets a coin balance in the wallet """
        return BinanceClient.get_asset_balance(asset=coin)

    @classmethod
    def buy_order(cls, symbol):
        try:
            wallet_balance = BinanceClient.get_asset_balance(
                asset="USDT").get("free")
            wallet_balance = float(wallet_balance)
            order_details = BinanceClient.create_order(
                symbol=symbol,
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quoteOrderQty=wallet_balance
            )
            return order_details
        except Exception as e:
            print("Buy Exception>>>>", e.__dict__)

    @classmethod
    def sell_order(cls, symbol):
        try:
            coin = symbol.split("USDT")[0]
            coin_balance = BinanceClient.get_asset_balance(
                asset=coin).get("free")
            coin_balance = round(float(coin_balance) * 0.999, 6)
            order_details = BinanceClient.create_order(
                symbol=symbol,
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=coin_balance
            )
            return order_details
        except Exception as e:
            print("Sell Exception>>>>", e.__dict__)

    @classmethod
    def orders(cls):
        BinanceClient.get_all_orders()
