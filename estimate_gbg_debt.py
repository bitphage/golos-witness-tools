#!/usr/bin/env python

import argparse
import logging
import sys
import yaml

from piston import Steem
from piston.amount import Amount
from piston.converter import Converter

log = logging.getLogger(sys.argv[0])


def get_median_price(steem_instance):
    """ get current median GBG/GOLOS price from network
    """

    cv = Converter(steem_instance)
    try:
        price = cv.sbd_median_price()
    except Exception as e:
        log.error(e)
        return False

    log.debug('current median price: %s', price)
    return price


def main():

    parser = argparse.ArgumentParser(
            description='Estimate GBG debt values',
            epilog='Report bugs to: https://github.com/bitfag/golos-witness-tools/issues')
    parser.add_argument('-d', '--debug', action='store_true',
            help='enable debug output'),
    parser.add_argument('-c', '--config', default='./common.yml',
            help='specify custom path for config file')
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

    golos = Steem(nodes=conf['node'], nobroadcast=True)
    props = golos.info()

    sbd_supply = Amount(props['current_sbd_supply'])
    current_supply = Amount(props['current_supply'])
    virtual_supply = Amount(props['virtual_supply'])

    median = get_median_price(golos)

    # libraries/chain/database.cpp
    # this min_price caps system debt to 10% of GOLOS market capitalisation
    min_price = 9 * sbd_supply.amount / current_supply.amount
    log.info('min_price GBG/GOLOS possible: {:.3f}'.format(min_price))

    # #define STEEMIT_100_PERCENT 10000
    # this is current GBG percent printed
    percent_sbd = sbd_supply.amount / median * 100 / virtual_supply.amount
    log.info('percent GBG: {:.3f}'.format(percent_sbd))
    log.info('GBG print rate: {:.2f}'.format(props['sbd_print_rate']/100))

if __name__ == '__main__':
    main()
