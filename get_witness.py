#!/usr/bin/env python

import argparse
import logging
import yaml

from pprint import pprint
from golos import Steem
from golos.witness import Witness

log = logging.getLogger('functions')

def main():

    parser = argparse.ArgumentParser(
            description='get witness info',
            epilog='Report bugs to https://github.com/bitfag/golos-witness-tools/issues')
    parser.add_argument('-c', '--config', default='./update_witness.yml',
            help='specify custom path for config file')
    parser.add_argument('witness',
            help='witness name to get info about')

    verbosity_args = parser.add_mutually_exclusive_group()
    verbosity_args.add_argument('-q', '--quiet', action='store_true',
        help='do not show any output except errors'),
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

    w = Witness(args.witness, steemd_instance=golos)
    pprint(w)


if __name__ == '__main__':
    main()
