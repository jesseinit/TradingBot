from datetime import datetime
import json

from decouple import config
from flask_mail import Message
from main import mail

ALLOWED_MAILS = config(
    'MAIL_ADDRS',
    cast=lambda emails: [email.strip() for email in emails.split(',')])


class MailHelper:
    @classmethod
    def send_ai_incoming_mail(cls, *args, **kwargs):
        recieved_at = kwargs.get('recieved_at')
        coin_name = kwargs.get('coin_name')
        details = kwargs.get('details')
        price = json.loads(kwargs.get('details'))['price']

        # <p>Received At: {recieved_at.strftime("%d %B, %Y, %H:%M:%S")}</p>
        ai_incoming_data_template = f"""
        <html lang="en">
        <body>
            <h3>Incoming AI Data - {coin_name} at {price} </h3>
            <hr>
            <p>Received At: {recieved_at}</p>
            <p>Coin Name: {coin_name}</p>
            <p>AI Details: {details}</p>
        </body>
        </html>
        """
        msg = Message("Incoming AI Data",
                      recipients=ALLOWED_MAILS,
                      html=ai_incoming_data_template)
        mail.send(msg)

    @classmethod
    def send_success_buy_mail(cls, order_details):
        email_template = f"""
        <html lang="en">
        <body>
            <h3>Successfull Buy Order</h3>
            <hr>
            <p>Completed At: {datetime.fromtimestamp(int(str(order_details.get('time', order_details.get('transactTime')))[:10])).strftime('%d %B, %Y, %H:%M:%S')}</p>
            <p>Symbol: {order_details['symbol']}</p>
            <p>Order Id: {order_details['orderId']}</p>
            <p>Orig Qty: {order_details['origQty']}</p>
            <p>Executed Qty: {order_details['executedQty']}</p>
            <p>Cummulative Quote Qty: {order_details['cummulativeQuoteQty']}</p>
            <p>Order Status: {order_details['status']}</p>
            <p>Time In Force: {order_details['timeInForce']}</p>
            <p>Type: {order_details['type']}</p>
            <p>Side: {order_details['side']}</p>
            <p>Price: {order_details['price']}</p>
            <p>Max Filled Price: {max(list(map(lambda fill: fill['price'], order_details['fills']))) if order_details.get('fills') else order_details.get('price')}</p>
            <p>Min Filled Price: {min(list(map(lambda fill: fill['price'], order_details['fills']))) if order_details.get('fills') else order_details.get('price')}</p>
        </body>
        </html>
        """
        bought_at = max(list(map(lambda fill: fill['price'], order_details['fills']))) if order_details.get(
            'fills') else order_details.get('price')
        msg = Message(
            f"Successfully Bought {order_details['symbol']} at {bought_at}",
            recipients=ALLOWED_MAILS,
            html=email_template)
        mail.send(msg)

    @classmethod
    def send_success_sell_mail(cls, order_details):
        email_template = f"""
        <html lang="en">
        <body>
            <h3>Successfull Sell Order</h3>
            <hr>
            <p>Completed At: {datetime.fromtimestamp(int(str(order_details.get('time', order_details.get('transactTime')))[:10])).strftime('%d %B, %Y, %H:%M:%S')}</p>
            <p>Symbol: {order_details['symbol']}</p>
            <p>Order Id: {order_details['orderId']}</p>
            <p>Orig Qty: {order_details['origQty']}</p>
            <p>Executed Qty: {order_details['executedQty']}</p>
            <p>Cummulative Quote Qty: {order_details['cummulativeQuoteQty']}</p>
            <p>Order Status: {order_details['status']}</p>
            <p>Time In Force: {order_details['timeInForce']}</p>
            <p>Type: {order_details['type']}</p>
            <p>Side: {order_details['side']}</p>
            <p>Max Filled Price: {max(list(map(lambda fill: fill['price'], order_details['fills']))) if order_details.get('fills') else order_details.get('price')}</p>
            <p>Min Filled Price: {min(list(map(lambda fill: fill['price'], order_details['fills']))) if order_details.get('fills') else order_details.get('price')}</p>
        </body>
        </html>
        """
        sold_at = max(list(map(lambda fill: fill['price'], order_details['fills']))) if order_details.get(
            'fills') else order_details.get('price')
        msg = Message(
            f"Successfully Sold {order_details['symbol']} at {sold_at}",
            recipients=ALLOWED_MAILS,
            html=email_template)
        mail.send(msg)

    @classmethod
    def send_cancel_mail(cls, order_details):
        email_template = f"""
        <html lang="en">
        <body>
            <h3>Successfull Cancelled Order</h3>
            <p>The buy limit order was not filled in the alloted time of 2mins</p>
            <hr>
            <p>Completed At: {datetime.fromtimestamp(int(str(order_details['transactTime'])[:10])).strftime('%d %B, %Y, %H:%M:%S')}</p>
            <p>Symbol: {order_details['symbol']}</p>
            <p>Order Id: {order_details['orderId']}</p>
            <p>Orig Qty: {order_details['origQty']}</p>
            <p>Executed Qty: {order_details['executedQty']}</p>
            <p>Cummulative Quote Qty: {order_details['cummulativeQuoteQty']}</p>
            <p>Order Status: {order_details['status']}</p>
            <p>Time In Force: {order_details['timeInForce']}</p>
            <p>Type: {order_details['type']}</p>
            <p>Side: {order_details['side']}</p>
        </body>
        </html>
        """
        msg = Message(
            f"Successfully Cancelled {order_details['symbol']} with ID - {order_details['orderId']}",
            recipients=ALLOWED_MAILS,
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
                      recipients=ALLOWED_MAILS,
                      html=email_template)
        mail.send(msg)
