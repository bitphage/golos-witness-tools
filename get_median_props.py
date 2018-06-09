#!/usr/bin/env python

import argparse
import logging
import yaml

from pprint import pprint
from golos import Steem

log = logging.getLogger('functions')

def main():

    parser = argparse.ArgumentParser(
            description='get current median properties',
            epilog='Report bugs to https://github.com/bitfag/golos-witness-tools/issues')
    parser.add_argument('-c', '--config', default='./common.yml',
            help='specify custom path for config file')
    parser.add_argument('-d', '--debug', action='store_true',
            help='enable debug output'),
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
        conf = yaml.load(ymlfile)

    # initialize steem instance
    golos = Steem(nodes=conf['node'], keys=conf['keys'])

    median_props = golos.get_chain_properties()
    pprint(median_props)


if __name__ == '__main__':
    main()
