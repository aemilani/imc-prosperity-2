import jsonpickle
import string
import numpy as np
from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List


class Trader:
    def run(self, state: TradingState):
        conversions = 0
        traderData = 'SAMPLE'

        # Trading -----------------------------------------------------------------------------------------------------
        result = {}

        # GIFT_BASKET -------------------------------------------------------------------------------------------------
        if ('CHOCOLATE' in state.order_depths) and ('STRAWBERRIES' in state.order_depths) and\
                ('ROSES' in state.order_depths) and ('GIFT_BASKET' in state.order_depths):

            products = ['CHOCOLATE', 'STRAWBERRIES', 'ROSES', 'GIFT_BASKET']
            product_weight = {'CHOCOLATE': 3, 'STRAWBERRIES': 5, 'ROSES': 1, 'GIFT_BASKET': 1}
            max_positions = {'CHOCOLATE': 250, 'STRAWBERRIES': 350, 'ROSES': 60, 'GIFT_BASKET': 60}

            def get_position(prod: str) -> int:
                if prod in state.position:
                    if state.position[prod]:
                        position: int = state.position[prod]
                    else:
                        position = 0
                else:
                    position = 0
                return position

            def trade_product(product: str, size: int) -> None:
                orders: List[Order] = []
                order_depth: OrderDepth = state.order_depths[product]
                if size > 0:
                    buy_size = size
                    for i in range(len(order_depth.sell_orders)):
                        ask, ask_amount = list(order_depth.sell_orders.items())[i]
                        curr_size = min(buy_size, -ask_amount)
                        print(f"BUY {product}", str(curr_size) + "x", ask)
                        orders.append(Order(product, ask, curr_size))
                        buy_size -= curr_size
                elif size < 0:
                    sell_size = size
                    for i in range(len(order_depth.buy_orders)):
                        bid, bid_amount = list(order_depth.buy_orders.items())[i]
                        curr_size = max(sell_size, -bid_amount)
                        print(f"SELL {product}", str(curr_size) + "x", bid)
                        orders.append(Order(product, bid, curr_size))
                        sell_size -= curr_size
                result[product].extend(orders)

            def trade_comp(size: int) -> None:
                for product in ['CHOCOLATE', 'STRAWBERRIES', 'ROSES']:
                    orders: List[Order] = []
                    order_depth: OrderDepth = state.order_depths[product]
                    if size > 0:
                        buy_size = size * product_weight[product]
                        for i in range(len(order_depth.sell_orders)):
                            ask, ask_amount = list(order_depth.sell_orders.items())[i]
                            curr_size = min(buy_size, -ask_amount)
                            print(f"BUY {product}", str(curr_size) + "x", ask)
                            orders.append(Order(product, ask, curr_size))
                            buy_size -= curr_size
                    elif size < 0:
                        sell_size = size * product_weight[product]
                        for i in range(len(order_depth.buy_orders)):
                            bid, bid_amount = list(order_depth.buy_orders.items())[i]
                            curr_size = max(sell_size, -bid_amount)
                            print(f"SELL {product}", str(curr_size) + "x", bid)
                            orders.append(Order(product, bid, curr_size))
                            sell_size -= curr_size
                    result[product].extend(orders)

            def trade_gift(size: int) -> None:
                product = 'GIFT_BASKET'
                orders: List[Order] = []
                order_depth: OrderDepth = state.order_depths[product]
                if size > 0:
                    buy_size = size * product_weight[product]
                    for i in range(len(order_depth.sell_orders)):
                        ask, ask_amount = list(order_depth.sell_orders.items())[i]
                        curr_size = min(buy_size, -ask_amount)
                        print(f"BUY {product}", str(curr_size) + "x", ask)
                        orders.append(Order(product, ask, curr_size))
                        buy_size -= curr_size
                elif size < 0:
                    sell_size = size * product_weight[product]
                    for i in range(len(order_depth.buy_orders)):
                        bid, bid_amount = list(order_depth.buy_orders.items())[i]
                        curr_size = max(sell_size, -bid_amount)
                        print(f"SELL {product}", str(curr_size) + "x", bid)
                        orders.append(Order(product, bid, curr_size))
                        sell_size -= curr_size
                result[product].extend(orders)

            mid_prices, available_bid_sizes, available_ask_sizes, max_buy_sizes, max_sell_sizes = {}, {}, {}, {}, {}
            for product in products:
                result[product] = []

                curr_position = get_position(product)
                print(f'{product} position: {curr_position}')

                order_depth: OrderDepth = state.order_depths[product]

                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                mid_prices[product] = (best_bid + best_ask) / 2

                # available_bid_size = 0
                # for i in range(len(order_depth.buy_orders)):
                #     bid, bid_amount = list(order_depth.buy_orders.items())[i]
                #     available_bid_size += bid_amount
                bid, available_bid_size = list(order_depth.buy_orders.items())[0]
                available_bid_sizes[product] = available_bid_size

                # available_ask_size = 0
                # for i in range(len(order_depth.sell_orders)):
                #     ask, ask_amount = list(order_depth.sell_orders.items())[i]
                #     available_ask_size += ask_amount
                ask, available_ask_size = list(order_depth.sell_orders.items())[0]
                available_ask_sizes[product] = available_ask_size

                max_position = max_positions[product]
                max_buy_size = max_position - curr_position
                max_buy_size = min(max_buy_size, -available_ask_size)
                max_sell_size = -max_position - curr_position
                max_sell_size = max(max_sell_size, -available_bid_size)
                max_buy_sizes[product] = max_buy_size
                max_sell_sizes[product] = max_sell_size

            available_bid_sizes['COMPOSITE'] = min(available_bid_sizes['CHOCOLATE'] // product_weight['CHOCOLATE'],
                                                   available_bid_sizes['STRAWBERRIES'] // product_weight['STRAWBERRIES'],
                                                   available_bid_sizes['ROSES'] // product_weight['ROSES'])
            available_ask_sizes['COMPOSITE'] = max(available_ask_sizes['CHOCOLATE'] // product_weight['CHOCOLATE'],
                                                   available_ask_sizes['STRAWBERRIES'] // product_weight['STRAWBERRIES'],
                                                   available_ask_sizes['ROSES'] // product_weight['ROSES'])
            max_buy_sizes['COMPOSITE'] = min(max_buy_sizes['CHOCOLATE'] // product_weight['CHOCOLATE'],
                                             max_buy_sizes['STRAWBERRIES'] // product_weight['STRAWBERRIES'],
                                             max_buy_sizes['ROSES'] // product_weight['ROSES'])
            max_sell_sizes['COMPOSITE'] = max(max_sell_sizes['CHOCOLATE'] // product_weight['CHOCOLATE'],
                                              max_sell_sizes['STRAWBERRIES'] // product_weight['STRAWBERRIES'],
                                              max_sell_sizes['ROSES'] // product_weight['ROSES'])

            gift = mid_prices['GIFT_BASKET']
            comp = mid_prices['CHOCOLATE'] * product_weight['CHOCOLATE'] +\
                       mid_prices['STRAWBERRIES'] * product_weight['STRAWBERRIES'] +\
                       mid_prices['ROSES'] * product_weight['ROSES']
            ratio = gift / comp
            ratio_mean = 1.2110
            ratio_std = 0.0013
            print(f'Ratio: {ratio}')

            param_fair_diff = 0.1
            param_thr = 1.2
            fair_ratio_high = ratio_mean + param_fair_diff * ratio_std
            fair_ratio_low = ratio_mean - param_fair_diff * ratio_std
            thr_high = ratio_mean + param_thr * ratio_std
            thr_low = ratio_mean - param_thr * ratio_std

            # Market taking
            if ratio < thr_low:  # buy GIFT_BASKET, sell COMPOSITE
                size_gift = min(max_buy_sizes['GIFT_BASKET'], -max_sell_sizes['COMPOSITE'] / ratio)
                size_comp = -ratio * size_gift
                # size_gift = int(size_gift)
                # size_comp = int(size_comp)
                size_gift = int(size_gift)
                size_comp = int(size_comp)
                if (size_gift != 0) and (size_comp != 0):
                    print(f'BUY {size_gift} GIFT_BASKET')
                    print(f'SELL {size_comp} COMPOSITE')
                    trade_gift(size_gift)
                    trade_comp(size_comp)

            elif ratio > thr_high:  # sell GIFT_BASKET, buy COMPOSITE
                size_gift = max(max_sell_sizes['GIFT_BASKET'], -max_buy_sizes['COMPOSITE'] / ratio)
                size_comp = -ratio * size_gift
                # size_gift = int(size_gift)
                # size_comp = int(size_comp)
                size_gift = int(size_gift)
                size_comp = int(size_comp)
                if (size_gift != 0) and (size_comp != 0):
                    print(f'SELL {size_gift} GIFT_BASKET')
                    print(f'BUY {size_comp} COMPOSITE')
                    trade_gift(size_gift)
                    trade_comp(size_comp)

            elif fair_ratio_low < ratio < fair_ratio_high:  # liquidate positions
                for product in products:
                    position = get_position(product)
                    trade_product(product, -position)

        return result, conversions, traderData