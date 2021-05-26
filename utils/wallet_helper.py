import math

from binance.client import Client
from binance.enums import ORDER_TYPE_MARKET, SIDE_BUY, SIDE_SELL
from decouple import config
from main import logger

CURRENT_ENV = config('FLASK_ENV')
BINANCE_API_KEY = config("BINANCE_API_KEY")
BINANCE_API_SECRET = config("BINANCE_API_SECRET")

BinanceClient = Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)


class Wallet:
    """ Manages all operations to be performed on a binance wallet """

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
            logger.info(f'ATTEMPTING A BUY FOR>>> {symbol}')
            wallet_balance = BinanceClient.get_asset_balance(
                asset="USDT").get("free")
            wallet_balance = float(wallet_balance)
            order_details = BinanceClient.create_order(
                symbol=symbol,
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quoteOrderQty=wallet_balance
            )
            logger.info(f'COMPLETED A BUY FOR>>> {symbol}', extra={
                        "custom_dimensions": order_details})
            return order_details
        except Exception as e:
            properties = {'custom_dimensions': dict(
                request=e.request, response=e.response.__dict__, exception=e.__dict__)}
            logger.exception(
                f'ERROR OCCURED BUYING>>> {symbol}', extra=properties)
            logger.warning(f'FAILED A BUY FOR>>> {symbol}')

    @classmethod
    def sell_order(cls, symbol):
        try:
            logger.info(f'ATTEMPTING A SELL FOR>>> {symbol}')
            coin = symbol.split("USDT")[0]
            coin_balance = BinanceClient.get_asset_balance(
                asset=coin).get("free")
            symbol_info = BinanceClient.get_symbol_info(symbol=symbol)
            step_size = float(symbol_info['filters'][2]['stepSize'])
            precision = int(round(-math.log(step_size, 10), 0))
            coin_balance = float(coin_balance)
            final_quantity = round(coin_balance, precision)
            order_details = BinanceClient.create_order(
                symbol=symbol,
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=final_quantity
            )
            logger.info(f'COMPLETED A SELL FOR>>> {symbol}', extra={
                        "custom_dimensions": order_details})

            return order_details
        except Exception as e:
            properties = {'custom_dimensions': e}
            logger.exception(
                f'ERROR OCCURED SELLING>>> {symbol}', extra=properties)
            max_allowed_qty = round(final_quantity * 0.998, precision)
            next_coin_value = round(coin_balance * 0.999, precision)

            if e.message == 'Filter failure: LOT_SIZE' or e.message == 'Account has insufficient balance for requested action.':
                logger.warning(f'ERROR TYPE>>> {e.message}')
                retry_status = True
                while retry_status:
                    try:
                        logger.info(
                            f"RETYING SELL ORDER WITH {next_coin_value} which is {round((next_coin_value/coin_balance) * 100, 2)}% of {coin_balance}")
                        order_details = BinanceClient.create_order(
                            symbol=symbol,
                            side=SIDE_SELL,
                            type=ORDER_TYPE_MARKET,
                            quantity=next_coin_value
                        )

                        retry_status = False

                        logger.info(
                            f"SELL ORDER COMPLETED WITH {round((next_coin_value/coin_balance) * 100, 2)}% of {coin_balance} which is {next_coin_value}>>>")

                        logger.info(f'COMPLETED A SELL FOR>>> {symbol}', extra={
                                    "custom_dimensions": order_details})

                        return order_details
                    except:
                        if e.message == 'Filter failure: LOT_SIZE' or e.message == 'Account has insufficient balance for requested action.':
                            logger.info("RECOMPUTING COIN VALUE>>>")
                            next_coin_value = round(
                                next_coin_value * 0.999, precision)
                            if next_coin_value <= max_allowed_qty:
                                # Send mail to hugo about failed retry status
                                logger.info(
                                    f"STOPPED RETRY LOGIC - WE CANNOT GO MORE THAN {max_allowed_qty} CURRENTLY {next_coin_value}>>>")
                                break

            if e.status_code >= 500:
                # Implement 3 trials
                # Send mail to hugo about binana
                logger.exception(
                    f'ERROR OCCURED SELLING>>> {symbol}', extra=properties)

    @classmethod
    def retry_sell_order(cls, symbol):
        # Todo - Extract retry logic to this function
        pass
