import sys
from pprint import pprint
from loguru import logger
from helpers import TradingHelper
import json
from constants import Message

logger.add(sys.stderr, format='{time} {level} {message}', level="INFO")


class Trade:

    def __init__(self):
        self.helper = TradingHelper()

    def main(self):
        logger.debug('Getting the instruments...')
        instruments = json.loads(self.helper.get_instruments())
        logger.debug('Please choose your instrument for trading from the following ones')
        for instrument in instruments:
            logger.debug(instrument.get('name'))
        instrument = input('Enter your instrument: ')
        return self.trade(instrument) if self.helper.validate_instrument(instrument, instruments) else \
            self.helper.warn(Message.instrument)

    def trade(self, instrument):
        side = input('Choose your side (buy or sell)')
        return self.set_quantity(instrument, side) if self.helper.validate_side(side) else \
            self.helper.warn(Message.side)

    def set_quantity(self, instrument: str, side: str):
        quantity = input('Set your quantity (decimal)')
        return self.make_rfq(instrument, quantity, side) if self.helper.validate_quantity(quantity) else \
            self.helper.warn(Message.quantity)

    def make_rfq(self, instrument: str, quantity: str, side: str):
        logger.info('Waiting for rfq data...')
        rfq_response = json.loads(self.helper.get_rfq(instrument, side, quantity))
        logger.info('This is your rfq data. Please confirm your trade action in 15 seconds')
        pprint(rfq_response)
        confirmation = input(' Please confirm your trade action (yes/no)')
        return self.trade_rfq(rfq_response) if self.helper.validate_confirmation(confirmation) else \
            self.helper.warn(Message.confirmation)

    def trade_rfq(self, rfq_response):
        logger.info('Your trade information')
        pprint(json.loads(self.helper.trade(rfq_response)))
        logger.info('Balance is')
        pprint(json.loads(self.helper.get_balance()))


if __name__ == '__main__':
    trader = Trade()
    trader.main()
