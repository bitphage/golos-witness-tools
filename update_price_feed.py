#!/usr/bin/env python

# This script is inspired by roelandp script https://github.com/roelandp/golospricefeed

import sys
import argparse
import logging
import yaml
from golos import Steem

from functions import *

log = logging.getLogger('functions')


def calculate_gbg_golos_price():

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
    price_btc_gold = price_mg_gold/usd_btc
    log.info('BTC/gold: {:.8f}'.format(price_btc_gold))

    # BTC/GBG / BTC/gold rate just for analytics
    gbg_gold_rate = price_btc_gbg/price_btc_gold
    log.info('GBG/gold rate: {:.2f}'.format(gbg_gold_rate))

    # calculated price USD/golos just for analytics
    price_usd_golos = btc_golos * usd_btc
    log.info('USD/GOLOS: {:.2f}'.format(price_usd_golos))

    # how many mgs of gold in 1 GOLOS == GOLOS/GBG (1 GBG == 1 mg gold)
    price_gold_golos = price_usd_golos / price_mg_gold
    log.info('GBG/GOLOS: {:.3f}'.format(price_gold_golos))

    return price_gold_golos

def main():

    parser = argparse.ArgumentParser(
            description='golos price feed updater',
            epilog='Report bugs to https://github.com/bitfag/golos-witness-tools/issues')
    parser.add_argument('-c', '--config', default='./update_price_feed.yml',
            help='specify custom path for config file')
    parser.add_argument('-m', '--monitor', action='store_true',
            help='run in continuous mode and update price periodically')

    publish_args = parser.add_mutually_exclusive_group()
    publish_args.add_argument('-n', '--dry-run', action='store_true',
            help='calculate prices but do not send transaction to golos network')
    publish_args.add_argument('-f', '--force', action='store_true',
            help='force update price feed')

    verbosity_args = parser.add_mutually_exclusive_group()
    verbosity_args.add_argument('-q', '--quiet', action='store_true',
        help='do not show any output except errors, just silently update price feed'),
    verbosity_args.add_argument('-d', '--debug', action='store_true',
        help='enable debug output'),
    args = parser.parse_args()

    # create logger
    if args.quiet == True:
        log.setLevel(logging.ERROR)
    elif args.debug == True:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    log.addHandler(handler)

    # parse config
    with open(args.config, 'r') as ymlfile:
        conf = yaml.load(ymlfile)

    # initialize steem instance
    golos = Steem(nodes=conf['node'], keys=conf['keys'])

    # main loop
    while True:
        # flag variable which determine should we actually update price or not
        need_publish = False

        try:
            # request current witness info
            witness_data = get_witness(golos, conf['witness'])

            # calculate prices
            price = calculate_gbg_golos_price()
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
            diff = abs(old_price - price)
            if diff > conf['threshold']:
                log.info('publishing price, difference is: {:.3f}'.format(diff))
                need_publish = True
            else:
                log.debug('price difference is too low, not publishing price')

            # finally publish price if needed
            if need_publish == True or args.force == True:
                if args.dry_run and args.force == False:
                    log.info('--dry-run mode, not publishing price feed')
                else:
                    publish_price(golos, price, account=conf['witness'])

        except Exception as e:
            log.error('exception in main loop: %s', e)

        finally:

            if args.monitor:
                time.sleep(conf['interval'])
            else:
                sys.exit(0)

if __name__ == '__main__':
    main()
