import jsonpickle
import string
import numpy as np
from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List


class Trader:
    def run(self, state: TradingState):
        conversions = 0
        # Retrieve previous state -------------------------------------------------------------------------------------
        if state.traderData:
            try:
                previous_state = jsonpickle.decode(state.traderData)
                bids = previous_state.get('bids', {})
                asks = previous_state.get('asks', {})
            except Exception:
                print('JSON Decode error encountered.')
                bids = {}
                asks = {}
        else:
            bids = {}
            asks = {}

        # Print traderData and Observations ---------------------------------------------------------------------------
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))

        # Run the loop per product ------------------------------------------------------------------------------------
        result = {}
        for product in state.order_depths:
            if product not in bids:
                bids[product] = []
            if product not in asks:
                asks[product] = []

            order_depth: OrderDepth = state.order_depths[product]
            print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(
                len(order_depth.sell_orders)))

            if product in state.position:
                if state.position[product]:
                    curr_position: int = state.position[product]
                else:
                    curr_position = 0
            else:
                curr_position = 0

            orders: List[Order] = []

            if len(order_depth.buy_orders) != 0:
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
            else:
                best_bid, best_bid_amount = None, None
            if len(order_depth.sell_orders) != 0:
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
            else:
                best_ask, best_ask_amount = None, None

            bids[product].append(best_bid)
            asks[product].append(best_ask)

            # AMETHYSTS -----------------------------------------------------------------------------------------------
            if product == 'AMETHYSTS':
                fair_value = 10000
                print("Acceptable price : " + str(fair_value))
                max_position = 20

                max_buy_size = min(max_position, max_position - curr_position)
                max_sell_size = max(-max_position, -max_position - curr_position)

                # Market making ---------------------------------------------------------------------------------------
                thr_l = fair_value - 2
                thr_h = fair_value + 2
                buy_price = thr_l
                sell_price = thr_h

                if max_buy_size > 0:
                    print("BUY", str(max_buy_size) + "x", buy_price)
                    orders.append(Order(product, buy_price, max_buy_size))

                if max_sell_size < 0:
                    print("SELL", str(max_sell_size) + "x", sell_price)
                    orders.append(Order(product, sell_price, max_sell_size))

            # STARFRUIT -----------------------------------------------------------------------------------------------
            elif product == 'STARFRUIT':
                max_position = 20
                max_buy_size = min(max_position, max_position - curr_position)
                max_sell_size = max(-max_position, -max_position - curr_position)

                # Market making ---------------------------------------------------------------------------------------
                bid_arr = np.array(bids[product])
                ask_arr = np.array(asks[product])

                w_roll = 9
                if len(bid_arr) >= w_roll:
                    mid_arr = (bid_arr + ask_arr) / 2
                    mid_ma = mid_arr[-w_roll:].mean()
                    fair_value = mid_ma

                    if max_buy_size > 0:
                        buy_price = int(np.floor(fair_value)) - 1
                        print("BUY", str(max_buy_size) + "x", buy_price)
                        orders.append(Order(product, buy_price, max_buy_size))

                    if max_sell_size < 0:
                        sell_price = int(np.ceil(fair_value)) + 1
                        print("SELL", str(max_sell_size) + "x", sell_price)
                        orders.append(Order(product, sell_price, max_sell_size))

            # ORCHIDS -------------------------------------------------------------------------------------------------
            elif product == 'ORCHIDS':
                max_position = 20
                max_buy_size = min(max_position, max_position - curr_position)
                max_sell_size = max(-max_position, -max_position - curr_position)

                storage_cost = 0.1  # per Orchid per timestamp

                bid_price = state.observations.conversionObservations['ORCHIDS'].bidPrice
                ask_price = state.observations.conversionObservations['ORCHIDS'].askPrice
                transport_fees = state.observations.conversionObservations['ORCHIDS'].transportFees
                export_tariff = state.observations.conversionObservations['ORCHIDS'].exportTariff
                import_tariff = state.observations.conversionObservations['ORCHIDS'].importTariff
                sunlight = state.observations.conversionObservations['ORCHIDS'].sunlight
                humidity = state.observations.conversionObservations['ORCHIDS'].humidity

                # south_data[product].append({'bid_price': bid_price, 'ask_price': ask_price,
                #                             'transport_fees': transport_fees, 'export_tariff': export_tariff,
                #                             'import_tariff': import_tariff, 'sunlight': sunlight, 'humidity': humidity})

                # Arbitrage -------------------------------------------------------------------------------------------
                effective_bid_price = bid_price - transport_fees - export_tariff
                effective_ask_price = ask_price + transport_fees + import_tariff

                bid_1, bid_1_amount = list(order_depth.buy_orders.items())[0]
                ask_1, ask_1_amount = list(order_depth.sell_orders.items())[0]

                if bid_1 > effective_ask_price:  # short
                    sell_size = min(max_sell_size, bid_1_amount)
                    print("SELL", str(sell_size) + "x", bid_1)
                    orders.append(Order(product, bid_1, sell_size))
                    conversions = sell_size
                elif ask_1 < effective_bid_price:  # long
                    buy_size = min(max_buy_size, ask_1_amount)
                    print("SELL", str(buy_size) + "x", ask_1)
                    orders.append(Order(product, ask_1, buy_size))
                    conversions = buy_size

            result[product] = orders

        traderData = jsonpickle.encode({"bids": bids, "asks": asks})

        return result, conversions, traderData