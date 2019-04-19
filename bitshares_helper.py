import math

from bitshares import BitShares
from bitshares.market import Market
from bitshares.asset import Asset


class BitSharesHelper:
    def __init__(self, node=None):
        self.bitshares = BitShares(node=node)
        self.fetch_depth = 50

    def _get_market(self, market):
        return Market(market, bitshares_instance=self.bitshares)

    def get_market_buy_price_pct_depth(self, market, depth_pct):
        """ Measure QUOTE volume and BASE/QUOTE price for [depth] percent deep starting from highest bid

            :param str market: market in format 'QUOTE/BASE'
            :param float depth_pct: depth percent (1-100) to measure volume and average price
            :return: tuple with ("price as float", volume) where volume is actual base or quote volume
        """
        if not depth_pct > 0:
            raise Exception('depth_pct should be greater than 0')

        market = self._get_market(market)

        market_orders = market.orderbook(self.fetch_depth)['bids']
        market_fee = market['base'].market_fee_percent

        if not market_orders:
            return (0, 0)

        highest_bid_price = market_orders[0]['price']
        stop_price = highest_bid_price / (1 + depth_pct / 100)
        quote_amount = 0
        base_amount = 0
        for order in market_orders:
            if order['price'] > stop_price:
                quote_amount += order['quote']['amount']
                base_amount += order['base']['amount']
            else:
                break

        quote_amount *= 1 + market_fee

        return (base_amount / quote_amount, quote_amount)

    def get_market_sell_price_pct_depth(self, market, depth_pct):
        """ Measure QUOTE volume and BASE/QUOTE price for [depth] percent deep starting from lowest ask

            :param str market: market in format 'QUOTE/BASE'
            :param float depth_pct: depth percent (1-100) to measure volume and average price
            :return: tuple with ("price as float", volume) where volume is actual base or quote volume
        """
        if not depth_pct > 0:
            raise Exception('depth_pct should be greater than 0')

        market = self._get_market(market)

        market_orders = market.orderbook(self.fetch_depth)['asks']
        market_fee = market['quote'].market_fee_percent

        if not market_orders:
            return (0, 0)

        lowest_ask_price = market_orders[0]['price']
        stop_price = lowest_ask_price * (1 + depth_pct / 100)
        quote_amount = 0
        base_amount = 0
        for order in market_orders:
            if order['price'] < stop_price:
                quote_amount += order['quote']['amount']
                base_amount += order['base']['amount']
            else:
                break

        quote_amount /= 1 + market_fee

        return (base_amount / quote_amount, quote_amount)

    def get_market_buy_price(self, market, quote_amount=0, base_amount=0):
        """ Returns the BASE/QUOTE price for which [depth] worth of QUOTE could be sold, enhanced with
            moving average or weighted moving average. Most of this method is taken from DEXBot

            :param str market: market in format 'QUOTE/BASE'
            :param float quote_amount:
            :param float base_amount:
            :return: tuple with ("price as float", volume) where volume is actual base or quote volume
        """
        market = self._get_market(market)

        # In case amount is not given, return price of the highest buy order on the market
        if quote_amount == 0 and base_amount == 0:
            raise Exception("quote_amount or base_amount must be given")

        # Like get_market_sell_price(), but defaulting to base_amount if both base and quote are specified.
        asset_amount = base_amount

        """ Since the purpose is never get both quote and base amounts, favor base amount if both given because
            this function is looking for buy price.
        """
        if base_amount > quote_amount:
            base = True
        else:
            asset_amount = quote_amount
            base = False

        market_orders = market.orderbook(self.fetch_depth)['bids']
        market_fee = market['base'].market_fee_percent

        target_amount = asset_amount * (1 + market_fee)

        quote_amount = 0
        base_amount = 0
        missing_amount = target_amount

        for order in market_orders:
            if base:
                # BASE amount was given
                if order['base']['amount'] <= missing_amount:
                    quote_amount += order['quote']['amount']
                    base_amount += order['base']['amount']
                    missing_amount -= order['base']['amount']
                else:
                    base_amount += missing_amount
                    quote_amount += missing_amount / order['price']
                    break
            elif not base:
                # QUOTE amount was given
                if order['quote']['amount'] <= missing_amount:
                    quote_amount += order['quote']['amount']
                    base_amount += order['base']['amount']
                    missing_amount -= order['quote']['amount']
                else:
                    base_amount += missing_amount * order['price']
                    quote_amount += missing_amount
                    break

        # Prevent division by zero
        if not quote_amount:
            return (0.0, 0)

        return (base_amount / quote_amount, base_amount if base else quote_amount)

    def get_market_sell_price(self, market, quote_amount=0, base_amount=0):
        """ Returns the BASE/QUOTE price for which [depth] worth of QUOTE could be bought, enhanced with
            moving average or weighted moving average. Most of this method is taken from DEXBot

            :param str market: market in format 'QUOTE/BASE'
            :param float quote_amount:
            :param float base_amount:
            :return: tuple with ("price as float", volume) where volume is actual base or quote volume
        """
        market = self._get_market(market)

        # In case amount is not given, return price of the highest buy order on the market
        if quote_amount == 0 and base_amount == 0:
            raise Exception("quote_amount or base_amount must be given")

        asset_amount = quote_amount
        """ Since the purpose is never get both quote and base amounts, favor quote amount if both given because
            this function is looking for sell price.
        """
        if quote_amount > base_amount:
            quote = True
        else:
            asset_amount = base_amount
            quote = False

        market_orders = market.orderbook(self.fetch_depth)['asks']
        market_fee = market['quote'].market_fee_percent

        target_amount = asset_amount * (1 + market_fee)

        quote_amount = 0
        base_amount = 0
        missing_amount = target_amount

        for order in market_orders:
            if quote:
                # QUOTE amount was given
                if order['quote']['amount'] <= missing_amount:
                    quote_amount += order['quote']['amount']
                    base_amount += order['base']['amount']
                    missing_amount -= order['quote']['amount']
                else:
                    base_amount += missing_amount * order['price']
                    quote_amount += missing_amount
                    break
            elif not quote:
                # BASE amount was given
                if order['base']['amount'] <= missing_amount:
                    quote_amount += order['quote']['amount']
                    base_amount += order['base']['amount']
                    missing_amount -= order['base']['amount']
                else:
                    base_amount += missing_amount
                    quote_amount += missing_amount / order['price']
                    break

        # Prevent division by zero
        if not quote_amount:
            return (0.0, 0)

        return (base_amount / quote_amount, quote_amount if quote else base_amount)

    def get_market_center_price(self, market, base_amount=0, quote_amount=0, depth_pct=0):
        """ Returns the center price of market.

            :param str market: market in format 'QUOTE/BASE'
            :param float base_amount:
            :param float quote_amount:
            :param float depth_pct: depth percent (1-100) to measure volume and average price
            :return: Tuple with market center price as float, volume in buy or sell side which is lower
        """
        center_price = None
        if depth_pct:
            # depth_pct has precedence over xxx_amount
            buy_price, buy_volume = self.get_market_buy_price_pct_depth(market, depth_pct=depth_pct)
            sell_price, sell_volume = self.get_market_sell_price_pct_depth(market, depth_pct=depth_pct)
        elif base_amount or quote_amount:
            buy_price, buy_volume = self.get_market_buy_price(
                market, quote_amount=quote_amount, base_amount=base_amount
            )
            sell_price, sell_volume = self.get_market_sell_price(
                market, quote_amount=quote_amount, base_amount=base_amount
            )
        elif depth_pct and (base_amount or quote_amount):
            raise Exception('depth_pct and (base_amount, quote_amount) are mutually exclusive')

        if (buy_price is None or buy_price == 0.0) or (sell_price is None or sell_price == 0.0):
            return (0, 0)

        center_price = buy_price * math.sqrt(sell_price / buy_price)

        return (center_price, min(buy_volume, sell_volume))

    def get_feed_price(self, asset):
        """ Get price data from feed

            :param str asset: name of the asset
            :return: price as float
            :rtype: float
        """
        asset = Asset(asset, bitshares_instance=self.bitshares)
        return float(asset.feed['settlement_price'])
