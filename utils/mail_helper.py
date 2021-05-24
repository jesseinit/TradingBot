from flask_mail import Message
from main import mail
from datetime import datetime
import json


class MailHelper:

    @classmethod
    def send_ai_incoming_mail(cls, recieved_at, coin_name, trigger_name, trigger_value):
        ai_incoming_data_template = f"""
        <html lang="en">
        <body>
            <h3>Incoming AI Data</h3>
            <hr>
            <p>Received At: {recieved_at.strftime("%d %B, %Y, %H:%M:%S")}</p>
            <p>Coin Name: {coin_name}</p>
            <p>Trigger Type: {trigger_name}</p>
            <p>Trigger Value: {trigger_value}</p>
        </body>
        </html>
        """
        msg = Message("Incoming AI Data",
                      recipients=["jesse@chc.capital", "hugo@chc.capital"],
                      html=ai_incoming_data_template)
        mail.send(msg)

    @classmethod
    def send_success_buy_mail(cls, order_details):
        email_template = f"""
        <html lang="en">
        <body>
            <h3>Successfull Buy Order</h3>
            <hr>
            <p>Completed At: {datetime.fromtimestamp(int(str(order_details['transactTime'])[:10])).strftime('%d %B, %Y, %H:%M:%S')}</p>
            <p>Symbol: {order_details['symbol']}</p>
            <p>Client Order Id: {order_details['clientOrderId']}</p>
            <p>Orig Qty: {order_details['origQty']}</p>
            <p>Executed Qty: {order_details['executedQty']}</p>
            <p>Cummulative Quote Qty: {order_details['cummulativeQuoteQty']}</p>
            <p>Order Status: {order_details['status']}</p>
            <p>Time In Force: {order_details['timeInForce']}</p>
            <p>Type: {order_details['type']}</p>
            <p>Side: {order_details['side']}</p>
            <p>Filled Prices: {', '.join(str(fill['price']) for fill in order_details['fills'])}</p>
        </body>
        </html>
        """
        msg = Message(f"Successfully Bought {order_details['symbol']} at {order_details['fills'][0]['price']}",
                      recipients=["jesse@chc.capital", "hugo@chc.capital"],
                      html=email_template)
        mail.send(msg)

    @classmethod
    def send_success_sell_mail(cls, order_details):
        email_template = f"""
        <html lang="en">
        <body>
            <h3>Successfull Sell Order</h3>
            <hr>
            <p>Completed At: {datetime.fromtimestamp(int(str(order_details['transactTime'])[:10])).strftime('%d %B, %Y, %H:%M:%S')}</p>
            <p>Symbol: {order_details['symbol']}</p>
            <p>Client Order Id: {order_details['clientOrderId']}</p>
            <p>Orig Qty: {order_details['origQty']}</p>
            <p>Executed Qty: {order_details['executedQty']}</p>
            <p>Cummulative Quote Qty: {order_details['cummulativeQuoteQty']}</p>
            <p>Order Status: {order_details['status']}</p>
            <p>Time In Force: {order_details['timeInForce']}</p>
            <p>Type: {order_details['type']}</p>
            <p>Side: {order_details['side']}</p>
            <p>Filled Prices: {', '.join(str(fill['price']) for fill in order_details['fills'])}</p>
        </body>
        </html>
        """
        msg = Message(f"Successfully Sold {order_details['symbol']} at {order_details['fills'][0]['price']}",
                      recipients=["jesse@chc.capital", "hugo@chc.capital"],
                      html=email_template)
        mail.send(msg)

    @classmethod
    def send_exception_mail(cls, exception_message):
        email_template = f"""
        <html lang="en">
        <body>
            <h3>Error Occured</h3>
            <p><stong>{exception_message}</strong><>
            <p>I'll add extra context about the error on this line 🤯</p>

        </body>
        </html>
        """
        msg = Message(f"Error Occured",
                      recipients=["jesse@chc.capital", "hugo@chc.capital"],
                      html=email_template)
        mail.send(msg)
