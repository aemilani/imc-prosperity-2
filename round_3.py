import jsonpickle
import string
import numpy as np
from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List


class Trader:
    def run(self, state: TradingState):
        conversions = 0
        traderData = 'SAMPLE'
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

        # Trading -----------------------------------------------------------------------------------------------------
        result = {}

        # AMETHYSTS ---------------------------------------------------------------------------------------------------
        if 'AMETHYSTS' in state.order_depths:
            product = 'AMETHYSTS'
            print(product)

            if product in state.position:
                if state.position[product]:
                    curr_position: int = state.position[product]
                else:
                    curr_position = 0
            else:
                curr_position = 0

            print(f'Current position: {curr_position}')

            fair_value = 10000
            max_position = 20

            max_buy_size = max_position - curr_position
            max_sell_size = -max_position - curr_position

            # Market making
            thr_l = fair_value - 2
            thr_h = fair_value + 2
            buy_price = thr_l
            sell_price = thr_h

            orders: List[Order] = []
            if max_buy_size > 0:
                print("BUY", str(max_buy_size) + "x", buy_price)
                orders.append(Order(product, buy_price, max_buy_size))
            if max_sell_size < 0:
                print("SELL", str(max_sell_size) + "x", sell_price)
                orders.append(Order(product, sell_price, max_sell_size))

            result[product] = orders

        # STARFRUIT ---------------------------------------------------------------------------------------------------
        if 'STARFRUIT' in state.order_depths:
            product = 'STARFRUIT'
            print(product)
            if product not in bids:
                bids[product] = []
            if product not in asks:
                asks[product] = []

            order_depth: OrderDepth = state.order_depths[product]

            if product in state.position:
                if state.position[product]:
                    curr_position: int = state.position[product]
                else:
                    curr_position = 0
            else:
                curr_position = 0

            print(f'Current position: {curr_position}')

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

            if len(bids[product]) > 100:
                bids[product] = bids[product][1:]
                asks[product] = asks[product][1:]

            traderData = jsonpickle.encode({"bids": bids, "asks": asks})

            max_position = 20
            max_buy_size = min(max_position, max_position - curr_position)
            max_sell_size = max(-max_position, -max_position - curr_position)

            # Market making
            bid_arr = np.array(bids[product])
            ask_arr = np.array(asks[product])

            orders: List[Order] = []
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

            result[product] = orders

        # ORCHIDS -----------------------------------------------------------------------------------------------------
        if 'ORCHIDS' in state.order_depths:
            product = 'ORCHIDS'
            print(product)

            order_depth: OrderDepth = state.order_depths[product]

            if product in state.position:
                if state.position[product]:
                    curr_position: int = state.position[product]
                else:
                    curr_position = 0
            else:
                curr_position = 0

            print(f'Current position: {curr_position}')

            conversions = -curr_position

            max_position = 100
            max_buy_size = max_position - curr_position
            max_sell_size = -max_position - curr_position

            bid_price = state.observations.conversionObservations['ORCHIDS'].bidPrice
            ask_price = state.observations.conversionObservations['ORCHIDS'].askPrice
            transport_fees = state.observations.conversionObservations['ORCHIDS'].transportFees
            export_tariff = state.observations.conversionObservations['ORCHIDS'].exportTariff
            import_tariff = state.observations.conversionObservations['ORCHIDS'].importTariff

            # Arbitrage
            effective_south_bid_price = bid_price - transport_fees - export_tariff
            effective_south_ask_price = ask_price + transport_fees + import_tariff

            north_bid_1, north_bid_1_amount = list(order_depth.buy_orders.items())[0]
            north_ask_1, north_ask_1_amount = list(order_depth.sell_orders.items())[0]

            orders: List[Order] = []
            if north_bid_1 > effective_south_ask_price:  # short
                sell_size = max(max_sell_size, -north_bid_1_amount)
                print("SELL", str(sell_size) + "x", north_bid_1)
                orders.append(Order(product, north_bid_1, sell_size))
            elif north_ask_1 < effective_south_bid_price:  # long
                buy_size = min(max_buy_size, -north_ask_1_amount)
                print("BUY", str(buy_size) + "x", north_ask_1)
                orders.append(Order(product, north_ask_1, buy_size))

            result[product] = orders

        # GIFT_BASKET -------------------------------------------------------------------------------------------------
        if ('CHOCOLATE' in state.order_depths) and ('STRAWBERRIES' in state.order_depths) and\
                ('ROSES' in state.order_depths) and ('GIFT_BASKET' in state.order_depths):

            products = ['CHOCOLATE', 'STRAWBERRIES', 'ROSES', 'GIFT_BASKET']
            product_ratios = {'CHOCOLATE': 4, 'STRAWBERRIES': 6, 'ROSES': 1, 'GIFT_BASKET': 1}
            max_positions = {'CHOCOLATE': 250, 'STRAWBERRIES': 350, 'ROSES': 60, 'GIFT_BASKET': 60}

            curr_positions, mid_prices = {}, {}
            available_bid_sizes, available_ask_sizes = {}, {}
            max_buy_sizes_ss, max_sell_sizes_ss = {}, {}
            for product in products:
                print(product)
                result[product] = []

                if product in state.position:
                    if state.position[product]:
                        curr_position: int = state.position[product]
                    else:
                        curr_position = 0
                else:
                    curr_position = 0
                curr_positions[product] = curr_position
                print(f'Current position: {curr_position}')

                order_depth: OrderDepth = state.order_depths[product]

                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                mid_prices[product] = (best_bid + best_ask) / 2

                available_bid_size = 0
                for i in range(len(order_depth.buy_orders)):
                    bid, bid_amount = list(order_depth.buy_orders.items())[i]
                    available_bid_size += bid_amount
                available_bid_sizes[product] = available_bid_size

                available_ask_size = 0
                for i in range(len(order_depth.sell_orders)):
                    ask, ask_amount = list(order_depth.sell_orders.items())[i]
                    available_ask_size += ask_amount
                available_ask_sizes[product] = available_ask_size

                max_position = max_positions[product]
                max_buy_size = max_position - curr_position
                max_buy_size = min(max_buy_size, -available_ask_size)
                max_sell_size = -max_position - curr_position
                max_sell_size = max(max_sell_size, -available_bid_size)

                max_buy_size_ss = 0
                for i in range(len(order_depth.sell_orders)):
                    ask, ask_amount = list(order_depth.sell_orders.items())[i]
                    size = min(max_buy_size, -ask_amount)
                    max_buy_size_ss += ask * size
                    max_buy_size -= size
                max_buy_sizes_ss[product] = max_buy_size_ss

                max_sell_size_ss = 0
                for i in range(len(order_depth.buy_orders)):
                    bid, bid_amount = list(order_depth.buy_orders.items())[i]
                    size = max(max_sell_size, -bid_amount)
                    max_sell_size_ss += bid * size
                    max_sell_size -= size
                max_sell_sizes_ss[product] = max_sell_size_ss

            # 1 GIFT_BASKET = 4 CHOCOLATE + 6 STRAWBERRIES + 1 ROSES
            unit_size_buy_comp_ss = min(max_buy_sizes_ss['CHOCOLATE'] // 4, max_buy_sizes_ss['STRAWBERRIES'] // 6,
                                        max_buy_sizes_ss['ROSES'])
            unit_size_buy_comp_ss = min(unit_size_buy_comp_ss, -max_sell_sizes_ss['GIFT_BASKET'] // 11)

            unit_size_sell_comp_ss = min(-max_sell_sizes_ss['CHOCOLATE'] // 4, -max_sell_sizes_ss['STRAWBERRIES'] // 6,
                                         -max_sell_sizes_ss['ROSES'])
            unit_size_sell_comp_ss = min(unit_size_sell_comp_ss, max_buy_sizes_ss['GIFT_BASKET'] // 11)

            mid = mid_prices['GIFT_BASKET']
            mid_eq = 4 * mid_prices['CHOCOLATE'] + 6 * mid_prices['STRAWBERRIES'] + mid_prices['ROSES']
            diff = mid - mid_eq
            diff_mean = 379.5
            diff_std = 76.4

            param_fair_diff = 0.29
            param_thr = 0.57
            fair_diff_high = diff_mean + param_fair_diff * diff_std
            fair_diff_low = diff_mean - param_fair_diff * diff_std
            thr_high = diff_mean + param_thr * diff_std
            thr_low = diff_mean - param_thr * diff_std

            # Market taking
            if diff < thr_low:  # sell COMPOSITE, buy GIFT_BASKET
                units = []
                for product in ['CHOCOLATE', 'STRAWBERRIES', 'ROSES']:
                    order_depth: OrderDepth = state.order_depths[product]
                    bid, bid_amount = list(order_depth.buy_orders.items())[0]
                    units.append(unit_size_sell_comp_ss * product_ratios[product] // bid)
                product = 'GIFT_BASKET'
                order_depth: OrderDepth = state.order_depths[product]
                ask, ask_amount = list(order_depth.sell_orders.items())[0]
                units.append(unit_size_sell_comp_ss // ask)
                min_unit = min(units)

                if min_unit >= 1:
                    for product in ['CHOCOLATE', 'STRAWBERRIES', 'ROSES']:
                        orders: List[Order] = []
                        order_depth: OrderDepth = state.order_depths[product]
                        sell_size_ss = -unit_size_sell_comp_ss * product_ratios[product]
                        for i in range(len(order_depth.buy_orders)):
                            bid, bid_amount = list(order_depth.buy_orders.items())[i]
                            size_ss = max(sell_size_ss, -bid_amount * bid)
                            size = size_ss // bid
                            print(f"SELL {product}", str(size) + "x", bid)
                            orders.append(Order(product, bid, size))
                            sell_size_ss -= size_ss
                        result[product].extend(orders)

                    product = 'GIFT_BASKET'
                    orders: List[Order] = []
                    order_depth: OrderDepth = state.order_depths[product]
                    buy_size_ss = unit_size_sell_comp_ss * 11
                    for i in range(len(order_depth.sell_orders)):
                        ask, ask_amount = list(order_depth.sell_orders.items())[i]
                        size_ss = min(buy_size_ss, -ask_amount * ask)
                        size = size_ss // ask
                        print(f"BUY {product}", str(size) + "x", ask)
                        orders.append(Order(product, ask, size))
                        buy_size_ss -= size_ss
                    result[product].extend(orders)

            elif diff > thr_high:  # buy COMPOSITE, sell GIFT_BASKET
                units = []
                for product in ['CHOCOLATE', 'STRAWBERRIES', 'ROSES']:
                    order_depth: OrderDepth = state.order_depths[product]
                    ask, ask_amount = list(order_depth.sell_orders.items())[0]
                    units.append(unit_size_buy_comp_ss * product_ratios[product] // ask)
                product = 'GIFT_BASKET'
                order_depth: OrderDepth = state.order_depths[product]
                bid, bid_amount = list(order_depth.buy_orders.items())[0]
                units.append(unit_size_buy_comp_ss // bid)
                min_unit = min(units)

                if min_unit >= 1:
                    for product in ['CHOCOLATE', 'STRAWBERRIES', 'ROSES']:
                        orders: List[Order] = []
                        order_depth: OrderDepth = state.order_depths[product]
                        buy_size_ss = unit_size_buy_comp_ss * product_ratios[product]
                        for i in range(len(order_depth.sell_orders)):
                            ask, ask_amount = list(order_depth.sell_orders.items())[i]
                            size_ss = min(buy_size_ss, -ask_amount * ask)
                            size = size_ss // ask
                            print(f"BUY {product}", str(size) + "x", ask)
                            orders.append(Order(product, ask, size))
                            buy_size_ss -= size_ss
                        result[product].extend(orders)

                    product = 'GIFT_BASKET'
                    orders: List[Order] = []
                    order_depth: OrderDepth = state.order_depths[product]
                    sell_size_ss = -unit_size_buy_comp_ss * 11
                    for i in range(len(order_depth.buy_orders)):
                        bid, bid_amount = list(order_depth.buy_orders.items())[i]
                        size_ss = max(sell_size_ss, -bid_amount * bid)
                        size = size_ss // bid
                        print(f"SELL {product}", str(size) + "x", bid)
                        orders.append(Order(product, bid, size))
                        sell_size_ss -= size_ss
                    result[product].extend(orders)

            elif fair_diff_low < diff < fair_diff_high:  # Liquidate positions
                if curr_positions['GIFT_BASKET'] < 0:  # sell COMPOSITE, buy GIFT_BASKET
                    ratio_available = min(available_ask_sizes['GIFT_BASKET'] / curr_positions['GIFT_BASKET'],
                                          available_bid_sizes['CHOCOLATE'] / curr_positions['CHOCOLATE'],
                                          available_bid_sizes['STRAWBERRIES'] / curr_positions['STRAWBERRIES'],
                                          available_bid_sizes['ROSES'] / curr_positions['ROSES'], 1)

                    for product in ['CHOCOLATE', 'STRAWBERRIES', 'ROSES']:  # sell
                        orders: List[Order] = []
                        order_depth: OrderDepth = state.order_depths[product]
                        curr_position = curr_positions[product]

                        sell_size = -int(ratio_available * curr_position)
                        for i in range(len(order_depth.buy_orders)):
                            bid, bid_amount = list(order_depth.buy_orders.items())[i]
                            size = max(sell_size, -bid_amount)
                            print(f"SELL {product}", str(size) + "x", bid)
                            orders.append(Order(product, bid, size))
                            sell_size -= size
                        result[product].extend(orders)

                    product = 'GIFT_BASKET'  # buy
                    orders: List[Order] = []
                    order_depth: OrderDepth = state.order_depths[product]
                    curr_position = curr_positions[product]

                    buy_size = -int(ratio_available * curr_position)
                    for i in range(len(order_depth.sell_orders)):
                        ask, ask_amount = list(order_depth.sell_orders.items())[i]
                        size = min(buy_size, -ask_amount)
                        print(f"BUY {product}", str(size) + "x", ask)
                        orders.append(Order(product, ask, size))
                        buy_size -= size
                    result[product].extend(orders)

                if curr_positions['GIFT_BASKET'] > 0:  # buy COMPOSITE, sell GIFT_BASKET
                    ratio_available = min(available_bid_sizes['GIFT_BASKET'] / curr_positions['GIFT_BASKET'],
                                          available_ask_sizes['CHOCOLATE'] / curr_positions['CHOCOLATE'],
                                          available_ask_sizes['STRAWBERRIES'] / curr_positions['STRAWBERRIES'],
                                          available_ask_sizes['ROSES'] / curr_positions['ROSES'], 1)

                    for product in ['CHOCOLATE', 'STRAWBERRIES', 'ROSES']:  # buy
                        orders: List[Order] = []
                        order_depth: OrderDepth = state.order_depths[product]
                        curr_position = curr_positions[product]

                        buy_size = -int(ratio_available * curr_position)
                        for i in range(len(order_depth.sell_orders)):
                            ask, ask_amount = list(order_depth.sell_orders.items())[i]
                            size = max(buy_size, -ask_amount)
                            print(f"BUY {product}", str(size) + "x", ask)
                            orders.append(Order(product, ask, size))
                            buy_size -= size
                        result[product].extend(orders)

                    product = 'GIFT_BASKET'  # sell
                    orders: List[Order] = []
                    order_depth: OrderDepth = state.order_depths[product]
                    curr_position = curr_positions[product]

                    sell_size = -int(ratio_available * curr_position)
                    for i in range(len(order_depth.buy_orders)):
                        bid, bid_amount = list(order_depth.buy_orders.items())[i]
                        size = max(sell_size, -bid_amount)
                        print(f"SELL {product}", str(size) + "x", bid)
                        orders.append(Order(product, bid, size))
                        sell_size -= size
                    result[product].extend(orders)

        return result, conversions, traderData