import math
import json
from typing import Literal
from binance.client import Client
from binance.enums import ORDER_TYPE_LIMIT, ORDER_TYPE_MARKET, SIDE_BUY, SIDE_SELL
from decouple import config
from main import logger

CURRENT_ENV = config('FLASK_ENV')
BINANCE_API_KEY = config("BINANCE_API_KEY")
BINANCE_API_SECRET = config("BINANCE_API_SECRET")

BinanceClient = Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)


class Wallet:
    """ Manages all operations to be performed on a binance wallet """

    WALLET_COINS = ["USDT", "ADA", "BTC", "EOS", "THETA", "TRX", "ZIL"]
    VALID_COINS_12H = ["ADA", "BTC", "EOS", "THETA", "TRX", "ZIL"]
    VALID_COINS_5M = ["XLM", "BTC", "LINK", "ETH", "ADA", "ETC"]

    @classmethod
    def retrieve_coin_balance(cls, coin: str = "USDT"):
        """ Gets a coin balance in the wallet """
        coins_details = BinanceClient.get_asset_balance(asset=coin)
        return coins_details

    # @classmethod
    # def buy_order(cls, symbol):
    #     try:
    #         logger.info(f'ATTEMPTING A BUY FOR>>> {symbol}')
    #         wallet_balance = BinanceClient.get_asset_balance(
    #             asset="USDT").get("free")
    #         wallet_balance = float(wallet_balance)
    #         order_details = BinanceClient.create_order(
    #             symbol=symbol,
    #             side=SIDE_BUY,
    #             type=ORDER_TYPE_MARKET,
    #             quoteOrderQty=wallet_balance)
    #         logger.info(f'COMPLETED A BUY FOR>>> {symbol}',
    #                     extra={"custom_dimensions": order_details})
    #         return order_details
    #     except Exception as e:
    #         properties = {
    #             'custom_dimensions':
    #             dict(request=e.request,
    #                  response=e.response.__dict__,
    #                  exception=e.__dict__)
    #         }
    #         logger.exception(f'ERROR OCCURED BUYING>>> {symbol}',
    #                          extra=properties)
    #         logger.warning(f'FAILED A BUY FOR>>> {symbol}')

    @classmethod
    def buy_limit_order(cls, symbol, price, mode: Literal['12h', '5m']):
        # ? if exhaust_balance is False use 50% - it means that we are not currently holding any coin so lets use halve of our balance
        # ? if exhaust_balance is True use 100% - it means that we are currently holding a coin and we should use 100%(the remaining 50%) of the wallet
        from tasks import check_order_status
        try:
            logger.info(f'ATTEMPTING A BUY FOR>>> {symbol}')
            wallet_status = BinanceClient.get_asset_balance(asset="USDT")
            wallet_free_balance = wallet_status.get("free")
            logger.info(
                f"CURRENT FREE WALLET BALANCE >>> {wallet_free_balance}")
            wallet_locked_balance = wallet_status.get("locked")

            symbol_info = BinanceClient.get_symbol_info(symbol=symbol)
            # print("symbol_info>>>", symbol_info)

            tick_size = float(symbol_info['filters'][0]['tickSize'])
            print("tick_size>>", tick_size)

            step_size = float(symbol_info['filters'][2]['stepSize'])

            precision = int(round(-math.log(step_size, 10), 0))

            minimum_buy_quantity = round(
                float(symbol_info['filters'][2]['minQty']), precision)
            print("minimum_qty>>", minimum_buy_quantity)

            min_allowed_coin_amount = float(
                symbol_info['filters'][3]['minNotional'])
            print("min_allowed_coin_amount>>>", min_allowed_coin_amount)

            wallet_locked_balance = round(
                float(wallet_locked_balance), precision)

            print("wallet_frozen_balance>>>>", wallet_locked_balance)

            # ? - We are using only 99.90 of our wallet balance
            wallet_free_balance = round(
                float(wallet_free_balance) * 0.999, precision)
            print("100% of Free Balance>>", wallet_free_balance)

            wallet_free_balance = wallet_free_balance * 0.5
            print("50% of Free Balance>>", wallet_free_balance)

            # Todo - when order was filled in the background and a new buy order came and we dont have any locked balance, we want to still use 100%. the currentt behaviour right now its going to use 50% since locked_balance (0) is not greater than min_allowed_coin_amount(10)
            if wallet_locked_balance >= min_allowed_coin_amount:
                # ? Use 100% of our 50% balance
                wallet_free_balance = round(
                    float(wallet_status.get("free")) * 0.999, precision)
                logger.info(
                    f'"USE 100% of free balance which is {wallet_free_balance} since a coin has been bought')
                print(
                    "USE 100% of Free Balance since a coin has been bought>>", wallet_free_balance)

            print("final_wallet_balance>>>", wallet_free_balance)

            # ? - Check to see that wallet_free_balance has enough balance to process the order
            if wallet_free_balance < min_allowed_coin_amount:
                logger.info(
                    f'Buy Order For {symbol} Aborted - Insufficient Wallet Balance at {wallet_free_balance}'
                )
                print("We dont have enough to make this order")
                return None

            # ? - At most any splitted order buy upto 5k worth or coins
            max_order_amount = config('MAX_ORDER_AMOUNT_PER_ORDER',
                                      cast=float,
                                      default=5000.0)

            # ? - The price we are willing to buy the coin at
            quoted_price = round(float(price), precision)

            # ? - The number of order splits we want to have
            order_iteration = int(wallet_free_balance / max_order_amount)
            print("order_iteration>>>", order_iteration)

            # ? - This loop generates amounts that each of the split order is goint to have
            buy_order_amounts = []
            for _ in range(order_iteration):
                # ? - Ensuring we dont go more than a certain limit
                if max_order_amount >= min_allowed_coin_amount:
                    buy_order_amounts.append(round(max_order_amount,
                                                   precision))
                    wallet_free_balance = wallet_free_balance - max_order_amount

                # ? - Ensuring we cater for amount that is less than the max order amount but still enough to better utilize our wallet balance
                if wallet_free_balance > min_allowed_coin_amount and max_order_amount > wallet_free_balance:
                    buy_order_amounts.append(
                        round(wallet_free_balance, precision))

            print("buy_order_amounts>>>>", buy_order_amounts)
            print("wallet_free_balance>>>>", wallet_free_balance)

            completed_orders = []
            for order_amount in buy_order_amounts:
                current_buy_quantity = round(order_amount / quoted_price,
                                             precision)

                # ? - Why are we incrementing the quoted price with the tick size
                quoted_price = round(quoted_price + tick_size, precision)
                print("current_buy_quantity>>>", current_buy_quantity)
                print("quoted_price>>>", quoted_price)

                try:
                    order_details = BinanceClient.order_limit_buy(
                        symbol=symbol,
                        quantity=current_buy_quantity,
                        price=quoted_price)
                    if order_details:
                        check_order_status.apply_async(kwargs={
                            "mode": mode,
                            "symbol":
                            symbol,
                            'order_id':
                            order_details.get('orderId'),
                        }, countdown=config('BG_DELAY', default=300, cast=int)
                        )
                        completed_orders.append(order_details)
                except Exception as e:
                    print("exception in for loop>>>", e)
                    logger.exception(
                        f'ERROR OCCURED BUYING - INSIDE LOOP>>> {symbol}', exc_info=e)
                    continue

            return completed_orders

        except Exception as e:
            print("exception>>>", e)
            logger.exception(f'ERROR OCCURED BUYING>>> {symbol}', exc_info=e)

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
            order_details = BinanceClient.create_order(symbol=symbol,
                                                       side=SIDE_SELL,
                                                       type=ORDER_TYPE_MARKET,
                                                       quantity=final_quantity)
            logger.info(f'COMPLETED A SELL FOR>>> {symbol}',
                        extra={"custom_dimensions": order_details})

            return order_details
        except Exception as e:
            properties = {'custom_dimensions': e}
            logger.exception(f'ERROR OCCURED SELLING>>> {symbol}',
                             extra=properties)
            max_allowed_qty = round(final_quantity * 0.998, precision)
            next_coin_value = round(coin_balance * 0.999, precision)

            if e.message in ['Account has insufficient balance for requested action.', 'Filter failure: LOT_SIZE']:
                logger.warning(f'ERROR TYPE>>> {e.message}')
                retry_status = True
                while retry_status:
                    try:
                        logger.info(
                            f"RETYING SELL ORDER WITH {next_coin_value} which is {round((next_coin_value/coin_balance) * 100, 2)}% of {coin_balance}"
                        )
                        order_details = BinanceClient.create_order(
                            symbol=symbol,
                            side=SIDE_SELL,
                            type=ORDER_TYPE_MARKET,
                            quantity=next_coin_value)

                        retry_status = False

                        logger.info(
                            f"SELL ORDER COMPLETED WITH {round((next_coin_value/coin_balance) * 100, 2)}% of {coin_balance} which is {next_coin_value}>>>"
                        )

                        logger.info(f'COMPLETED A SELL FOR>>> {symbol}',
                                    extra={"custom_dimensions": order_details})

                        return order_details
                    except:
                        if e.message in [
                                'Account has insufficient balance for requested action.',
                                'Filter failure: LOT_SIZE'
                        ]:
                            logger.info("RECOMPUTING COIN VALUE>>>")
                            next_coin_value = round(next_coin_value * 0.999,
                                                    precision)
                            if next_coin_value <= max_allowed_qty:
                                # Send mail to hugo about failed retry status
                                logger.info(
                                    f"STOPPED RETRY LOGIC - WE CANNOT GO MORE THAN {max_allowed_qty} CURRENTLY {next_coin_value}>>>"
                                )
                                break

            if e.status_code >= 500:
                # Implement 3 trials
                # Send mail to hugo about binana
                logger.exception(f'ERROR OCCURED SELLING>>> {symbol}',
                                 extra=properties)

    @classmethod
    def cancel_order(cls, symbol, order_id):
        logger.info(f"ATTEMPTING TO CANCEL THE ORDER WITH ID >>> {order_id}")
        cancelled_order = BinanceClient.cancel_order(symbol=symbol,
                                                     orderId=order_id)
        with open("cancelled_orders.log", 'a') as cancel_log:
            cancel_log.write(f"{json.dumps(cancelled_order)}\n\n")
        logger.info(f"CANCELLED THE ORDER WITH ID >>> {order_id} CANCELLED")
        return cancelled_order

    @classmethod
    def retrive_order_details(cls, symbol, order_id):
        logger.info(f"ATTEMPTING TO RETRIEVE THE ORDER WITH ID >>>{order_id}")
        order_details = BinanceClient.get_order(symbol=symbol,
                                                orderId=order_id)
        logger.info(f"RETRIEVED THE ORDER WITH ID >>>{order_id}")
        return order_details
