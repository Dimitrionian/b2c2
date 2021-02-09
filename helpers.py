import sys
import uuid
import decimal
import requests
from loguru import logger
from requests import exceptions
import datetime
import time

logger.add(sys.stderr, format='{time} {level} {message}', level="INFO")


def exception_handler(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except exceptions.ConnectionError as ex:
            logger.error(ex.args)
        except exceptions.HTTPError as ex:
            logger.error(ex.args)
        except exceptions.Timeout as ex:
            logger.error(ex.args)
        except exceptions.TooManyRedirects as ex:
            logger.error(ex.args)
        except AssertionError as ex:
            logger.error(ex.args)
        sys.exit('The program aborted')

    return inner


logger.add(sys.stderr, format='{time} {level} {message}', level="INFO")


class TradingHelper:
    def validate_instrument(self, instrument, instruments) -> bool:
        # linear complexity
        return instrument in [item.get('name') for item in instruments]

    def validate_side(self, side) -> bool:
        return side in ['buy', 'sell']

    def validate_quantity(self, quantity: str) -> bool:
        try:
            quantity = decimal.Decimal(quantity)
        except decimal.InvalidOperation as ex:
            return False
        return quantity > 0

    def validate_confirmation(self, confirmation) -> bool:
        return confirmation in ['yes', 'no']

    def warn(self, message):
        logger.debug(message)
        SystemExit()

    def get_instruments(self):
        response = self.get_response('https://api.uat.b2c2.net/instruments/')
        return response.content

    def get_rfq(self, instrument, side, quantity):
        client_rfq_id = str(uuid.uuid4())
        payload = {
            'instrument': instrument,
            'side': side,
            'quantity': quantity,
            'client_rfq_id': client_rfq_id
        }
        response = self.get_response('https://api.uat.b2c2.net/request_for_quote/', payload)
        return response.text

    def trade(self, rfq_response):
        payload = {
            'instrument': rfq_response['instrument'],
            'side': rfq_response['side'],
            'quantity': rfq_response['quantity'],
            'client_order_id': str(uuid.uuid4()),
            'price': rfq_response['price'],
            'order_type': 'FOK',
            'valid_until': datetime.datetime.utcfromtimestamp(time.time() + 10).strftime("%Y-%m-%dT%H:%M:%S"),
            'rfq_id': rfq_response['rfq_id'],
            'executing_unit': 'risk-adding-strategy'
        }
        response = self.get_response('https://api.uat.b2c2.net/order/', payload)
        return response.content

    def get_balance(self):
        response = self.get_response('https://api.uat.b2c2.net/balance/')
        return response.content

    @exception_handler
    def get_response(self, url, payload=None):
        # Token is hardcoded only in testing purposes, not appropriate in real tasks
        headers = {'Authorization': 'Token e13e627c49705f83cbe7b60389ac411b6f86fee7'}
        response = requests.get(url, headers=headers) if payload is None else \
            requests.post(url, data=payload, headers=headers)
        assert response.status_code != 403, response.content
        assert response.status_code != 401, response.content
        assert response.status_code != 400, response.content
        return response
