import json
import math
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
    def retrieve_coin_balance(cls, coin: str = "USDT"):
        """ Gets a coin balance in the wallet """
        coins_details = BinanceClient.get_asset_balance(asset=coin)
        return coins_details

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
            print("BUY ORDER COMPLETED>>>>", order_details)
            return order_details
        except Exception as e:
            print("Buy Exception>>>>", e.__dict__)

    @classmethod
    def sell_order(cls, symbol):
        try:
            coin = symbol.split("USDT")[0]
            coin_balance = BinanceClient.get_asset_balance(
                asset=coin).get("free")
            coin_balance = round(float(coin_balance), 5)
            print("coin_balance>>>>", coin_balance)
            order_details = BinanceClient.create_order(
                symbol=symbol,
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=coin_balance
            )
            print("SELL ORDER COMPLETED>>>>", order_details)
            return order_details
        except Exception as e:
            # print("Sell Exception HAPPENeD>>>>", e.__dict__)
            with open("sell_orders.log", 'a') as sell_exception_log:
                sell_exception_log.write(
                    f"Sell Exception HAPPENeD>>>> {e.__dict__}\n")
                # sell_log.write(f"{json.dumps(sell_order_details)}\n")
            max_allowed_coin_bal = round(float(coin_balance) * 0.900, 5)
            next_coin_value = round(float(coin_balance) * 0.999, 5)

            if e.status_code == 400 and (e.message == 'Filter failure: LOT_SIZE' or e.message == 'Account has insufficient balance for requested action.'):
                retry_status = True
                while retry_status:
                    try:
                        print(
                            f"RETYING SELL ORDER WITH {next_coin_value} which is {round((next_coin_value/coin_balance) * 100, 2)}% of {coin_balance}")

                        with open("sell_orders.log", 'a') as sell_exception_log:
                            sell_exception_log.write(
                                f"RETYING SELL ORDER WITH {next_coin_value} which is {round((next_coin_value/coin_balance) * 100, 2)}% of {coin_balance}\n\n")

                        order_details = BinanceClient.create_order(
                            symbol=symbol,
                            side=SIDE_SELL,
                            type=ORDER_TYPE_MARKET,
                            quantity=next_coin_value
                        )

                        retry_status = False
                        print(
                            f"SELL ORDER COMPLETED WITH {round((next_coin_value/coin_balance) * 100, 2)}% of {coin_balance} which is {next_coin_value}>>>")

                        print("SELL ORDER COMPLETED WITH>>>", order_details)

                        return order_details
                    except:
                        if e.status_code == 400 and (e.message == 'Filter failure: LOT_SIZE' or e.message == 'Account has insufficient balance for requested action.'):
                            print("RECOMPUTING COIN VALUE>>>")
                            next_coin_value = round(
                                float(next_coin_value) * 0.999, 5)
                            if next_coin_value <= max_allowed_coin_bal:
                                # retry_status = False
                                # Send mail to hugo about failed retry status
                                print("STOP RETRY>>>>")
                                break

            if e.status_code >= 500:
                # Implement 3 trials
                # Send mail to hugo about binana
                print("Sell Exception>>>>", e.__dict__)

    @classmethod
    def orders(cls):
        BinanceClient.get_all_orders()


def retry_logic():
    pass


#from utils.wallet_helper import Wallet
#buy_order_details = Wallet.buy_order(symbol=f"ETHUSDT")
#sell_order_details = Wallet.sell_order(symbol=f"ETHUSDT")


# def floatPrecision(f, n):
#     n = int(math.log10(1 / float(n)))
#     f = math.floor(float(f) * 10 * n) / 10 * n
#     f = "{:0.0{}f}".format(float(f), n)
#     return str(int(f)) if int(n) == 0 else f


# symbol_info = client.get_symbol_info('ETHUSDT')

# tick_size = float(filter(
#     lambda f: f['filterType'] == 'PRICE_FILTER', symbol_info['filters'])[0]['tickSize'])
# step_size = float(filter(
#     lambda f: f['filterType'] == 'LOT_SIZE', symbol_info['filters'])[0]['stepSize'])

# price = float(filter(lambda x: x['symbol'] ==
#               'ETHUSDT', client.get_all_tickers())[0]['price'])

# price = floatPrecision(price, tick_size)

# usdt_balance = float(client.get_asset_balance(asset='USDT'))

# quantity = floatPrecision(usdt_balance / float(price), step_size)
