#!/usr/bin/env python

import sys
import json
import argparse
import logging
import yaml
from datetime import datetime
from datetime import timedelta
from golos import Steem
from golos.amount import Amount

import functions

log = logging.getLogger('functions')


def main():

    parser = argparse.ArgumentParser(
        description='', epilog='Report bugs to: https://github.com/bitfag/golos-witness-tools/issues'
    )
    parser.add_argument('-d', '--debug', action='store_true', help='enable debug output'),
    parser.add_argument('-c', '--config', default='./common.yml', help='specify custom path for config file')
    args = parser.parse_args()

    # create logger
    if args.debug == True:
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

    golos = Steem(nodes=conf['node'])

    hist = golos.get_feed_history()['price_history']
    hist_size = len(hist)

    # median history contains values for STEEMIT_FEED_HISTORY_WINDOW
    # median price update performed once per hour

    for i in hist:

        timestamp = datetime.now() - timedelta(hours=hist_size)
        base = Amount(i['base'])
        quote = Amount(i['quote'])
        price = base.amount / quote.amount
        print('{}: {:.3f}'.format(timestamp.strftime('%d.%m.%Y %H'), price))
        # use hist_size as iterator
        hist_size -= 1


if __name__ == '__main__':
    main()
