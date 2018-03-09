#!/usr/bin/env python

import argparse
import logging
import sys
import yaml

from piston import Steem
from piston.amount import Amount

import functions

log = logging.getLogger('functions')

def main():

    parser = argparse.ArgumentParser(
            description='Estimate GBG debt values',
            epilog='Report bugs to: https://github.com/bitfag/golos-witness-tools/issues')
    parser.add_argument('-d', '--debug', action='store_true',
            help='enable debug output'),
    parser.add_argument('-c', '--config', default='./common.yml',
            help='specify custom path for config file')
    parser.add_argument('--usd', action='store_true',
            help='display debt points in USD')
    args = parser.parse_args()


    if args.debug == True:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    log.addHandler(handler)

    # parse config
    with open(args.config, 'r') as ymlfile:
        conf = yaml.load(ymlfile)

    golos = Steem(node=conf['node'], nobroadcast=True)
    props = golos.info()

    sbd_supply = Amount(props['current_sbd_supply'])
    current_supply = Amount(props['current_supply'])
    virtual_supply = Amount(props['virtual_supply'])
    total_reward_fund_steem = Amount(props['total_reward_fund_steem'])

    median = functions.get_median_price(golos)

    # libraries/chain/database.cpp
    # this min_price caps system debt to 10% of GOLOS market capitalisation
    min_price = 9 * sbd_supply.amount / current_supply.amount
    log.info('Minimal possible median price GBG/GOLOS: {:.3f}'.format(min_price))

    # #define STEEMIT_100_PERCENT 10000
    # this is current GBG percent printed
    percent_sbd = sbd_supply.amount / median * 100 / virtual_supply.amount
    log.info('System GBG debt percent: {:.3f}'.format(percent_sbd))

    sbd_print_rate = props['sbd_print_rate']/100
    gbg_emission = (total_reward_fund_steem.amount / 2) * median * sbd_print_rate / 100
    log.info('GBG print rate: {:.2f}'.format(sbd_print_rate))
    log.info('Approximate GBG emission per day: {:.0f}'.format(gbg_emission))

    # USD/gold price
    price_mg_gold = functions.get_price_gold()
    # USD/BTC
    usd_btc = functions.get_price_usd_btc()
    # BTC/GOLD
    price_btc_gold = price_mg_gold / usd_btc
    # BTC/GOLOS
    price_btc_golos = functions.get_price_btc_golos()
    # BTC/GBG, external
    price_btc_gbg = functions.get_price_btc_gbg()

    log.info('Median-derived price BTC/gold: {:.8f}'.format(price_btc_golos/median))
    log.info('External price BTC/gold: {:.8f}'.format(price_btc_gold))
    log.info('External price BTC/GBG: {:.8f}'.format(price_btc_gbg))
    log.info('GBG/gold rate: {:.2f}'.format(price_btc_gbg/price_btc_gold))
    log.info('Current external price BTC/GOLOS: {:.8f}'.format(price_btc_golos))

    # estimate reward fund size and price
    gbg_reward_fund_size_nominal = gbg_emission * price_btc_gold
    gbg_reward_fund_size_nominal_usd = gbg_reward_fund_size_nominal * usd_btc
    gbg_reward_fund_size = gbg_emission * price_btc_gbg
    gbg_reward_fund_size_usd = gbg_reward_fund_size * usd_btc

    golos_reward_fund = total_reward_fund_steem.amount/2 \
            + total_reward_fund_steem.amount/2 * (10000-sbd_print_rate)/10000
    golos_reward_fund_size = golos_reward_fund * price_btc_golos
    golos_reward_fund_size_usd = golos_reward_fund_size * usd_btc

    total_reward_fund_size = gbg_reward_fund_size + golos_reward_fund_size
    total_reward_fund_size_usd = gbg_reward_fund_size_usd + golos_reward_fund_size_usd

    if args.usd:
        log.info('GBG reward fund size (nominal): ${:.0f}'.format(gbg_reward_fund_size_nominal_usd))
        log.info('GBG reward fund size (market): ${:.0f}'.format(gbg_reward_fund_size_usd))
        log.info('GOLOS reward fund size: ${:.0f}'.format(golos_reward_fund_size_usd))
        log.info('Total reward fund size: ${:.0f}'.format(total_reward_fund_size_usd))
        log.info('Approximate USD/GOLOS price at 2%-debt point: {:.3f}'.format(price_mg_gold*min_price*5))
        log.info('Approximate USD/GOLOS price at 5%-debt point: {:.3f}'.format(price_mg_gold*min_price*2))
        log.info('Approximate USD/GOLOS price at 10%-debt point: {:.3f}'.format(price_mg_gold*min_price))
    else:
        log.info('GBG reward fund size (nominal): {:.8f} BTC'.format(gbg_reward_fund_size_nominal))
        log.info('GBG reward fund size (market): {:.8f} BTC'.format(gbg_reward_fund_size))
        log.info('GOLOS reward fund size: {:.8f} BTC'.format(golos_reward_fund_size))
        log.info('Total reward fund size: {:.8f} BTC'.format(total_reward_fund_size))
        log.info('Approximate BTC/GOLOS price at 2%-debt point: {:.8f}'.format(price_btc_gold*min_price*5))
        log.info('Approximate BTC/GOLOS price at 5%-debt point: {:.8f}'.format(price_btc_gold*min_price*2))
        log.info('Approximate BTC/GOLOS price at 10%-debt point: {:.8f}'.format(price_btc_gold*min_price))

if __name__ == '__main__':
    main()
