import jsonpickle
import string
import numpy as np
from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List


class Trader:
    def run(self, state: TradingState):
        result = {}

        bid_price = state.observations.conversionObservations['ORCHIDS'].bidPrice
        ask_price = state.observations.conversionObservations['ORCHIDS'].askPrice
        transport_fees = state.observations.conversionObservations['ORCHIDS'].transportFees
        export_tariff = state.observations.conversionObservations['ORCHIDS'].exportTariff
        import_tariff = state.observations.conversionObservations['ORCHIDS'].importTariff
        sunlight = state.observations.conversionObservations['ORCHIDS'].sunlight
        humidity = state.observations.conversionObservations['ORCHIDS'].humidity

        data_json = jsonpickle.encode({'bid_price': bid_price, 'ask_price': ask_price, 'transport_fees': transport_fees,
                           'export_tariff': export_tariff, 'import_tariff': import_tariff,
                           'sunlight': sunlight, 'humidity': humidity})
        print(data_json)

        traderData = 'SAMPLE'
        conversions = 0
        return result, conversions, traderData