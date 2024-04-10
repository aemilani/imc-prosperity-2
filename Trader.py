import jsonpickle
import string
import numpy as np
from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List


class Trader:
    def run(self, state: TradingState):
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

        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))

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

            if product == 'AMETHYSTS':
                fair_value = 10000
                print("Acceptable price : " + str(fair_value))
                max_position = 20

                max_buy_size = min(max_position, max_position - curr_position)
                max_sell_size = max(-max_position, -max_position - curr_position)

                thr_l = fair_value - 2
                thr_h = fair_value + 2
                buy_price = thr_l
                sell_price = thr_h

                print("BUY", str(max_buy_size) + "x", buy_price)
                orders.append(Order(product, buy_price, max_buy_size))

                print("SELL", str(max_sell_size) + "x", sell_price)
                orders.append(Order(product, sell_price, max_sell_size))

            elif product == 'STARFRUIT':
                max_position = 20
                max_buy_size = min(max_position, max_position - curr_position)
                max_sell_size = max(-max_position, -max_position - curr_position)

                w_roll = 9
                std_mul = 0

                if len(bids[product]) >= w_roll:
                    bid_arr = np.array(bids[product])
                    ask_arr = np.array(asks[product])
                    mid_arr = (bid_arr + ask_arr) / 2
                    bol_h = mid_arr[-w_roll:].mean() + std_mul * mid_arr[-w_roll:].std()
                    bol_l = mid_arr[-w_roll:].mean() - std_mul * mid_arr[-w_roll:].std()
                    bol_m = (bol_h + bol_l) / 2

                    if (curr_position == 0) and (best_ask <= bol_l):
                        size = min(max_buy_size, -best_ask_amount)
                        print("BUY", str(size) + "x", best_ask)
                        orders.append(Order(product, best_ask, size))
                    if (curr_position == 0) and (best_bid >= bol_h):
                        size = max(max_sell_size, -best_bid_amount)
                        print("SELL", str(size) + "x", best_bid)
                        orders.append(Order(product, best_bid, size))
                    if curr_position < 0:
                        print("BUY", str(-curr_position) + "x", int(bol_m))
                        orders.append(Order(product, int(bol_m), -curr_position))
                    if curr_position > 0:
                        print("SELL", str(-curr_position) + "x", int(bol_m))
                        orders.append(Order(product, int(bol_m), -curr_position))

            result[product] = orders

            # String value holding Trader state data required.
        # It will be delivered as TradingState.traderData on next execution.

        traderData = jsonpickle.encode({"bids": bids, "asks": asks})

        # Sample conversion request. Check more details below.
        conversions = 1
        return result, conversions, traderData