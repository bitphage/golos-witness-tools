#!/usr/bin/env python

import argparse
import logging
import yaml
import statistics

from golos import Steem
from golos.witness import Witness


log = logging.getLogger('functions')


def get_median_voting(voting, sort_key):
    voting = sorted(voting, key=lambda k: k[sort_key])
    values = [i[sort_key] for i in voting]
    median = statistics.median(values)
    for el in voting:
        print('{name:<16} {min} {max}'.format(**el))
    log.info('%s median: %s', sort_key, median)

    next_voting = [e for e in voting if e[sort_key] == median]
    return next_voting


def main():

    parser = argparse.ArgumentParser(
        description='get voting props for curation percents',
        epilog='Report bugs to: https://github.com/bitfag/golos-witness-tools/issues',
    )
    parser.add_argument('-d', '--debug', action='store_true', help='enable debug output'),
    parser.add_argument('-c', '--config', default='./common.yml', help='specify custom path for config file')
    parser.add_argument('-C', '--count', default=19, help='number of witnesses to get')
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
        element = {
            'name': w['owner'],
            'min': w['props']['min_curation_percent'],
            'max': w['props']['max_curation_percent'],
        }
        voting.append(element)

    voting = sorted(voting, key=lambda k: k['min'])

    for key in ['min', 'max']:
        voting = get_median_voting(voting, key)


if __name__ == '__main__':
    main()
