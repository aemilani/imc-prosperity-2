from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string


class Trader:
    def run(self, state: TradingState):
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))

        result = {}
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(
                len(order_depth.sell_orders)))

            curr_position: int = state.position[product]

            orders: List[Order] = []

            if len(order_depth.buy_orders) != 0:
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
            else:
                best_bid, best_bid_amount = None, None
            if len(order_depth.sell_orders) != 0:
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
            else:
                best_ask, best_ask_amount = None, None

            if product == 'AMETHYSTS':
                fair_value = 10000
                print("Acceptable price : " + str(fair_value))
                max_position = 20
                max_buy_size = min(max_position, max_position - curr_position)
                max_sell_size = max(-max_position, -max_position - curr_position)
                thr_h = fair_value + 2
                thr_l = fair_value - 2
                if best_bid:
                    buy_price = min(thr_l, best_bid)
                else:
                    buy_price = thr_l
                if best_ask:
                    sell_price = max(thr_h, best_ask)
                else:
                    sell_price = thr_h

                print("BUY", str(max_buy_size) + "x", buy_price)
                orders.append(Order(product, buy_price, max_buy_size))

                print("SELL", str(max_sell_size) + "x", sell_price)
                orders.append(Order(product, sell_price, max_sell_size))

            elif product == 'STARFRUIT':
                pass
                # fair_value = 5000
                # print("Acceptable price : " + str(fair_value))
                # max_position = 20
                #
                # if best_ask and int(best_ask) < fair_value:
                #     print("BUY", str(-best_ask_amount) + "x", best_ask)
                #     orders.append(Order(product, best_ask, -best_ask_amount))
                #
                # if best_bid and int(best_bid) > fair_value:
                #     print("SELL", str(best_bid_amount) + "x", best_bid)
                #     orders.append(Order(product, best_bid, -best_bid_amount))

            result[product] = orders

            # String value holding Trader state data required.
        # It will be delivered as TradingState.traderData on next execution.
        traderData = "SAMPLE"

        # Sample conversion request. Check more details below.
        conversions = 1
        return result, conversions, traderData