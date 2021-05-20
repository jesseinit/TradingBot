import hashlib
import hmac
import time

import requests
from decouple import config


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
            return None

        return response.json()

     # Todo - Get USDT Balance
     # Todo - Add Swap Method
     # Todo - Retrieve the coin we are currently holding
