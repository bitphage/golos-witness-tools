#!/usr/bin/env python

import sys
import json
import argparse
import logging
import yaml
from piston import Steem
from pprint import pprint

import functions

log = logging.getLogger('functions')


def main():

    parser = argparse.ArgumentParser(
            description='get miner queue',
            epilog='Report bugs to: https://github.com/bitfag/golos-witness-tools/issues')
    parser.add_argument('-d', '--debug', action='store_true',
            help='enable debug output'),
    parser.add_argument('-c', '--config', default='./common.yml',
            help='specify custom path for config file')
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

    golos = Steem(node=conf['node'])

    q = golos.rpc.get_miner_queue(api='database_api')
    pprint(q)

if __name__ == '__main__':
    main()
