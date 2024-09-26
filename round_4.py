import jsonpickle
import math
import string
import numpy as np
from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List


class Trader:
    def run(self, state: TradingState):
        conversions = 0
        traderData = 'SAMPLE'

        def norm_cdf(x, mu=0, sigma=1):
            z = (x - mu) / (sigma * np.sqrt(2))
            return 0.5 * (1 + math.erf(z))

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

        # Retrieve previous state -------------------------------------------------------------------------------------
        if state.traderData:
            try:
                previous_state = jsonpickle.decode(state.traderData)
                bids = previous_state.get('bids', {})
                asks = previous_state.get('asks', {})
                mids = previous_state.get('mids', {})
            except Exception:
                print('JSON Decode error encountered.')
                bids = {}
                asks = {}
                mids = {}
        else:
            bids = {}
            asks = {}
            mids = {}

        # Trading -----------------------------------------------------------------------------------------------------
        result = {}

        # AMETHYSTS ---------------------------------------------------------------------------------------------------
        if 'AMETHYSTS' in state.order_depths:
            product = 'AMETHYSTS'

            curr_position = get_position(product)
            print(f'{product} position: {curr_position}')

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

            if product not in bids:
                bids[product] = []
            if product not in asks:
                asks[product] = []
            if product not in mids:
                mids[product] = []

            curr_position = get_position(product)
            print(f'{product} position: {curr_position}')

            order_depth: OrderDepth = state.order_depths[product]

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
            mids[product].append((best_bid + best_ask) / 2)

            if len(bids[product]) > 100:
                bids[product] = bids[product][1:]
                asks[product] = asks[product][1:]
                mids[product] = mids[product][1:]

            traderData = jsonpickle.encode({"bids": bids, "asks": asks, 'mids': mids})

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

            curr_position = get_position(product)
            print(f'{product} position: {curr_position}')

            order_depth: OrderDepth = state.order_depths[product]

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
            product_weight = {'CHOCOLATE': 3, 'STRAWBERRIES': 5, 'ROSES': 1, 'GIFT_BASKET': 1}
            max_positions = {'CHOCOLATE': 250, 'STRAWBERRIES': 350, 'ROSES': 60, 'GIFT_BASKET': 60}

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

            mid_prices, best_bid_sizes, best_ask_sizes, max_buy_sizes, max_sell_sizes = {}, {}, {}, {}, {}
            for product in products:
                result[product] = []

                curr_position = get_position(product)
                print(f'{product} position: {curr_position}')

                order_depth: OrderDepth = state.order_depths[product]

                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                mid_prices[product] = (best_bid + best_ask) / 2

                bid, best_bid_size = list(order_depth.buy_orders.items())[0]
                best_bid_sizes[product] = best_bid_size

                ask, best_ask_size = list(order_depth.sell_orders.items())[0]
                best_ask_sizes[product] = best_ask_size

                max_position = max_positions[product]
                max_buy_size = max_position - curr_position
                max_buy_size = min(max_buy_size, -best_ask_size)
                max_sell_size = -max_position - curr_position
                max_sell_size = max(max_sell_size, -best_bid_size)
                max_buy_sizes[product] = max_buy_size
                max_sell_sizes[product] = max_sell_size

            best_bid_sizes['COMPOSITE'] = min(best_bid_sizes['CHOCOLATE'] // product_weight['CHOCOLATE'],
                                              best_bid_sizes['STRAWBERRIES'] // product_weight['STRAWBERRIES'],
                                              best_bid_sizes['ROSES'] // product_weight['ROSES'])
            best_ask_sizes['COMPOSITE'] = max(best_ask_sizes['CHOCOLATE'] // product_weight['CHOCOLATE'],
                                              best_ask_sizes['STRAWBERRIES'] // product_weight['STRAWBERRIES'],
                                              best_ask_sizes['ROSES'] // product_weight['ROSES'])
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

        # COCONUT -----------------------------------------------------------------------------------------------------
        if ('COCONUT' in state.order_depths) and ('COCONUT_COUPON' in state.order_depths):
            # def calc_delta(curr_price, volatility, risk_free_rate):
            #     strike_price = 10000
            #     time_to_expiration = 250 / 365
            #     d1 = (np.log(curr_price / strike_price) + (
            #                 risk_free_rate + 0.5 * volatility ** 2) * time_to_expiration) / (
            #                      volatility * np.sqrt(time_to_expiration))
            #     return norm_cdf(d1)

            products = ['COCONUT', 'COCONUT_COUPON']
            max_positions = {'COCONUT': 300, 'COCONUT_COUPON': 600}

            for product in products:
                result[product] = []

                order_depth: OrderDepth = state.order_depths[product]
                if len(list(order_depth.buy_orders.items())) > 0:
                    best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                else:
                    best_bid, best_bid_amount = None, None
                if len(list(order_depth.sell_orders.items())) > 0:
                    best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                else:
                    best_ask, best_ask_amount = None, None

                if product not in bids:
                    bids[product] = []
                if product not in asks:
                    asks[product] = []
                if product not in mids:
                    mids[product] = []

                bids[product].append(best_bid)
                asks[product].append(best_ask)
                if best_bid and best_ask:
                    mids[product].append((best_bid + best_ask) / 2)
                elif best_bid and not best_ask:
                    mids[product].append(best_bid)
                elif best_ask and not best_bid:
                    mids[product].append(best_ask)
                else:
                    mids[product].append(None)

                if len(bids[product]) > 100:
                    bids[product] = bids[product][1:]
                    asks[product] = asks[product][1:]
                    mids[product] = mids[product][1:]

                traderData = jsonpickle.encode({"bids": bids, "asks": asks, 'mids': mids})

            # Market making
            product = 'COCONUT'
            result[product] = []
            curr_position = get_position(product)
            print(f'{product} position: {curr_position}')

            best_bid, best_ask = bids[product][-1], asks[product][-1]

            max_position = max_positions[product]
            max_buy_size = max_position - curr_position
            max_sell_size = -max_position - curr_position

            if best_bid and best_ask:
                orders: List[Order] = []
                if max_buy_size > 0:
                    print("BUY", str(max_buy_size) + "x", best_bid)
                    orders.append(Order(product, best_bid, max_buy_size))
                if max_sell_size < 0:
                    print("SELL", str(max_sell_size) + "x", best_ask)
                    orders.append(Order(product, best_ask, max_sell_size))
                result[product] = orders

            # Delta hedging
            asset_position = get_position('COCONUT')
            call_position = get_position('COCONUT_COUPON')

            # vol_mean = 0.1634
            # if len(bids['COCONUT']) < 100:
            #     vol = vol_mean
            # else:
            #     log_returns = np.log(np.array(mids['COCONUT'][1:]) / np.array(mids['COCONUT'][:-1]))
            #     vol = np.std(log_returns) * np.sqrt(10000 * 252)
            #     vol = (vol + 9 * vol_mean) / 10
            # vol = vol_mean

            delta_mean = 0.3943
            if len(bids['COCONUT']) < 100:
                delta = delta_mean
            else:
                d_asset = np.array(mids['COCONUT'][1:]) - np.array(mids['COCONUT'][:-1])
                d_call = np.array(mids['COCONUT_COUPON'][1:]) - np.array(mids['COCONUT_COUPON'][:-1])
                delta = d_call / d_asset
                delta[delta == np.inf] = delta_mean
                delta[delta == -np.inf] = delta_mean
                delta = np.nan_to_num(delta, nan=delta_mean)
                delta = np.mean(delta)
                delta = (delta + 9 * delta_mean) / 10

            # delta = (delta + calc_delta(curr_price=mids['COCONUT'][-1], volatility=vol, risk_free_rate=0.028)) / 2
            # delta = calc_delta(curr_price=mids['COCONUT'][-1], volatility=vol, risk_free_rate=0.03)
            print(f'Delta: {delta}')

            correct_call_position = -int(asset_position / delta)
            if correct_call_position < -max_positions['COCONUT_COUPON']:
                ratio = -max_positions['COCONUT_COUPON'] / correct_call_position
                trade_product('COCONUT', -int(ratio * asset_position))
                correct_call_position = -max_positions['COCONUT_COUPON']
                diff_call_position = correct_call_position - call_position
                trade_product('COCONUT_COUPON', diff_call_position)
            elif -max_positions['COCONUT_COUPON'] <= correct_call_position <= max_positions['COCONUT_COUPON']:
                diff_call_position = correct_call_position - call_position
                trade_product('COCONUT_COUPON', diff_call_position)
            else:
                ratio = max_positions['COCONUT_COUPON'] / correct_call_position
                trade_product('COCONUT', -int(ratio * asset_position))
                correct_call_position = max_positions['COCONUT_COUPON']
                diff_call_position = correct_call_position - call_position
                trade_product('COCONUT_COUPON', diff_call_position)

        return result, conversions, traderData