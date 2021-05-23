from binance.client import Client
from binance.enums import ORDER_TYPE_MARKET, SIDE_BUY, SIDE_SELL
from decouple import config
import math
from decimal import Decimal
import logging
logging.basicConfig(filename='example.log',
                    encoding='utf-8', level=logging.DEBUG)

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
            print("wallet_balance_before>>>", wallet_balance)
            order_details = BinanceClient.create_order(
                symbol=symbol,
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quoteOrderQty=wallet_balance
            )
            print("BUY ORDER COMPLETED>>>>", order_details)
            return order_details
        except Exception as e:
            print("Buy Exception>>>>", dict(request=e.request,
                  response=e.response.__dict__, exception=e.__dict__))

    @classmethod
    def sell_order(cls, symbol):
        try:
            coin = symbol.split("USDT")[0]
            coin_balance = BinanceClient.get_asset_balance(
                asset=coin).get("free")
            symbol_info = BinanceClient.get_symbol_info(symbol=symbol)
            step_size = float(symbol_info['filters'][2]['stepSize'])
            print("step_size>>>>", step_size)
            precision = int(round(-math.log(step_size, 10), 0))
            print("precision>>>>", precision)
            coin_balance = float(coin_balance)
            final_quantity = round(coin_balance, precision)
            print("coin_balance>>>>", coin_balance)
            print("final_quantity>>>>", final_quantity)

            order_details = BinanceClient.create_order(
                symbol=symbol,
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=final_quantity
            )

            print("SELL ORDER COMPLETED>>>>", order_details)
            wallet_balance = BinanceClient.get_asset_balance(
                asset="USDT").get("free")
            print("wallet_balance_after>>>", float(wallet_balance))
            return order_details
        except Exception as e:
            print("Sell Exception>>>>", e.__dict__)
            # print("Sell Exception>>>>", dict(request=e.request, response=e.response.__dict__, exception=e.__dict__))

            max_allowed_qty = round(final_quantity, precision)
            next_coin_value = round(coin_balance * 0.9999, precision)

            if e.message == 'Filter failure: LOT_SIZE' or e.message == 'Account has insufficient balance for requested action.':
                retry_status = True
                while retry_status:
                    try:
                        print(
                            f"RETYING SELL ORDER WITH {next_coin_value} which is {round((next_coin_value/coin_balance) * 100, 2)}% of {coin_balance}")

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
                        if e.message == 'Filter failure: LOT_SIZE' or e.message == 'Account has insufficient balance for requested action.':
                            print("RECOMPUTING COIN VALUE>>>")
                            next_coin_value = round(
                                next_coin_value * 0.9999, precision)
                            if next_coin_value <= max_allowed_qty:
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


# from utils.wallet_helper import Wallet, BinanceClient
# buy_order_details = Wallet.buy_order(symbol=f"ETHUSDT")
# sell_order_details = Wallet.sell_order(symbol=f"ETHUSDT")
# BinanceClient.get_symbol_info(symbol="ETHUSDT")['filters']
