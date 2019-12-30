#!/usr/bin/env python

import argparse
import logging
import yaml

from golos import Steem
from golos.witness import Witness

log = logging.getLogger(__name__)


def main():

    parser = argparse.ArgumentParser(
        description='get witness voting for a particular param',
        epilog='Report bugs to: https://github.com/bitfag/golos-witness-tools/issues',
    )
    parser.add_argument('-d', '--debug', action='store_true', help='enable debug output'),
    parser.add_argument('-c', '--config', default='./common.yml', help='specify custom path for config file')
    parser.add_argument('property', help='chain property to get voting for'),
    args = parser.parse_args()

    # create logger
    if args.debug is True:
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

    witnesses = golos.get_active_witnesses()
    witnesses = [Witness(w, steemd_instance=golos) for w in witnesses]
    voting = []

    for w in witnesses:
        element = {'name': w['owner'], 'property': w['props'][args.property]}
        voting.append(element)

    voting = sorted(voting, key=lambda k: k['property'])
    median = voting[10]['property']
    for el in voting:
        print('{name:<16} {property}'.format(**el))
    log.info('%s median: %s', args.property, median)


if __name__ == '__main__':
    main()
