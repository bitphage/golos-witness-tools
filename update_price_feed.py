#!/usr/bin/env python

# This script is inspired by roelandp script https://github.com/roelandp/golospricefeed

import sys
import argparse
import logging
import yaml
import statistics
import time

from golos import Steem
from bitshares_helper import BitSharesHelper

from functions import (
    get_price_gold,
    get_price_usd_btc,
    get_price_btc_golos,
    get_price_btc_gbg,
    split_pair,
    calc_weighted_average_price,
    get_witness,
    get_old_price,
    get_median_price,
    last_price_too_old,
    publish_price,
)

log = logging.getLogger('functions')


def calculate_gbg_golos_price_cmc():
    """ Old method to calculate price using coinmarketcap
    """

    # market price USD/gold
    price_mg_gold = get_price_gold()
    log.info('USD/gold: {:.4f}'.format(price_mg_gold))

    # market price USD/BTC
    usd_btc = get_price_usd_btc()
    log.info('USD/BTC: {:.0f}'.format(usd_btc))

    # market price BTC/GOLOS
    btc_golos = get_price_btc_golos()
    log.info('BTC/GOLOS: {:.8f}'.format(btc_golos))

    # market price BTC/GBG just for analytics
    price_btc_gbg = get_price_btc_gbg()
    log.info('BTC/GBG: {:.8f}'.format(price_btc_gbg))

    # calculated price BTC/gold just for analytics
    price_btc_gold = price_mg_gold / usd_btc
    log.info('BTC/gold: {:.8f}'.format(price_btc_gold))

    # BTC/GBG / BTC/gold rate just for analytics
    gbg_gold_rate = price_btc_gbg / price_btc_gold
    log.info('GBG/gold rate: {:.2f}'.format(gbg_gold_rate))

    # calculated price USD/golos just for analytics
    price_usd_golos = btc_golos * usd_btc
    log.info('USD/GOLOS: {:.2f}'.format(price_usd_golos))

    # how many mgs of gold in 1 GOLOS == GOLOS/GBG (1 GBG == 1 mg gold)
    price_gold_golos = price_usd_golos / price_mg_gold
    log.info('GBG/GOLOS: {:.3f}'.format(price_gold_golos))

    return price_gold_golos


def calculate_gbg_golos_price_bts(bitshares, markets, metric='median', depth_pct=20):
    """ Calculate price GBG/GOLOS

        :param BitSharesHelper bitshares:
        :param list markets: list of markets to use to obtain price, in format ['QUOTE/BASE']
        :param str metric: what metric to use to calculate price
        :param float depth_pct: how deeply measure market for volume
        :return: price
        :rtype: float
    """

    prices = []
    price_bts_golos = 0

    assert markets is not None

    for market in markets:
        quote, base = split_pair(market)
        # Price and volume on GOLOS/XXX market
        price1, volume1 = bitshares.get_market_center_price(market, depth_pct=20)
        log.info('Raw price {:.8f} {}/{}'.format(price1, base, quote))

        # Price and volume on XXX/BTS market
        if base != 'BTS':
            tmp_market = '{}/BTS'.format(base)
            price2, volume2 = bitshares.get_market_center_price(tmp_market, depth_pct=20)
            price = price1 * price2
            # Limit volume by smallest volume across steps
            volume = min(volume1, volume2 / price1)
        else:
            price, volume = price1, volume1

        log.debug('Derived price BTS/GOLOS from market {}: {:.8f}, volume: {:.0f}'.format(market, price, volume))
        prices.append({'price': price, 'volume': volume, 'market': market})

    price_list = [v for element in prices for k, v in element.items() if k == 'price']
    price_bts_golos_median = statistics.median(price_list)
    log.info('Median market price: {:.8f} BTS/GOLOS'.format(price_bts_golos_median))
    price_bts_golos_mean = statistics.mean(price_list)
    log.info('Mean market price: {:.8f} BTS/GOLOS'.format(price_bts_golos_mean))
    price_bts_golos_wa = calc_weighted_average_price(prices)
    log.info('Weighted average market price: {:.8f} BTS/GOLOS'.format(price_bts_golos_wa))

    if metric == 'median':
        price_bts_golos = price_bts_golos_median
    elif metric == 'mean':
        price_bts_golos = price_bts_golos_mean
    elif metric == 'weighted_average':
        price_bts_golos = price_bts_golos_wa
    else:
        log.critical('unsupported metric')
        sys.exit(1)

    # 1 GOLD is 1 troy ounce; calc xxx GOLD for 1 BTS
    price_troyounce = bitshares.get_feed_price('GOLD')
    gram_in_troyounce = 31.1034768
    # How many 1mg gold for 1 BTS
    price_gold_bts = price_troyounce * gram_in_troyounce * 1000
    log.debug('Gold price is: {:.8f} 1mgGOLD/BTS'.format(price_gold_bts))

    price_gold_golos = price_bts_golos * price_gold_bts
    log.info('Calculated price {:.3f} GBG/GOLOS'.format(price_gold_golos))

    return price_gold_golos


def main():

    parser = argparse.ArgumentParser(
        description='golos price feed updater',
        epilog='Report bugs to https://github.com/bitfag/golos-witness-tools/issues',
    )
    parser.add_argument('-c', '--config', default='./update_price_feed.yml', help='specify custom path for config file')
    parser.add_argument(
        '-m', '--monitor', action='store_true', help='run in continuous mode and update price periodically'
    )

    publish_args = parser.add_mutually_exclusive_group()
    publish_args.add_argument(
        '-n', '--dry-run', action='store_true', help='calculate prices but do not send transaction to golos network'
    )
    publish_args.add_argument('-f', '--force', action='store_true', help='force update price feed')

    verbosity_args = parser.add_mutually_exclusive_group()
    verbosity_args.add_argument(
        '-q',
        '--quiet',
        action='store_true',
        help='do not show any output except errors, just silently update price feed',
    ),
    verbosity_args.add_argument('-d', '--debug', action='store_true', help='enable debug output'),
    args = parser.parse_args()

    # create logger
    if args.quiet:
        log.setLevel(logging.ERROR)
    elif args.debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    log.addHandler(handler)

    # parse config
    with open(args.config, 'r') as ymlfile:
        conf = yaml.safe_load(ymlfile)

    # defaults
    price_source = conf.get('source', 'bitshares')
    metric = conf.get('metric', 'median')
    depth_pct = conf.get('depth_pct', 20)
    threshold_pct = conf.get('threshold_pct', 10) / 100

    # initialize steem instance
    golos = Steem(nodes=conf['node'], keys=conf['keys'])

    if price_source == 'bitshares':
        bitshares = BitSharesHelper(node=conf['node_bts'])

    # main loop
    while True:
        # flag variable which determine should we actually update price or not
        need_publish = False

        try:
            # request current witness info
            witness_data = get_witness(golos, conf['witness'])

            # calculate prices
            if price_source == 'bitshares':
                price = calculate_gbg_golos_price_bts(bitshares, conf['markets'], metric=metric, depth_pct=depth_pct)
            elif price_source == 'cmc':
                price = calculate_gbg_golos_price_cmc()

            old_price = get_old_price(witness_data)
            median_price = get_median_price(golos)
            log.info('Current median price: {:.3f}'.format(median_price))

            # apply correction if k defined
            if 'k' in conf:
                price = price * conf['k']
                log.info('price after correction: {:.3f}'.format(price))

            # check whether our price is too old
            last_price_update_too_old = last_price_too_old(witness_data, conf['max_age'])
            if last_price_update_too_old:
                log.info('Our last price update older than max_age, forcing update')
                need_publish = True

            # check for price difference between our old price and new price
            diff_rel = abs((old_price / price) - 1)
            if diff_rel > threshold_pct:
                log.info('publishing price, difference is: {:.2%}'.format(diff_rel))
                need_publish = True
            else:
                log.debug('price difference is too low, not publishing price')

            # finally publish price if needed
            if need_publish or args.force:
                if args.dry_run:
                    log.info('--dry-run mode, not publishing price feed')
                else:
                    publish_price(golos, price, account=conf['witness'])

        except Exception:
            log.exception('exception in main loop:')

        finally:

            if args.monitor:
                time.sleep(conf['interval'])
            else:
                sys.exit(0)


if __name__ == '__main__':
    main()
