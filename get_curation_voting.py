#!/usr/bin/env python

import sys
import json
import argparse
import logging
import yaml
from golos import Steem

import functions

log = logging.getLogger('functions')


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

    witnesses = golos.get_witnesses_by_vote('', args.count)
    voting = []

    for w in witnesses:
        element = {
            'name': w['owner'],
            'min': w['props']['min_curation_percent'],
            'max': w['props']['max_curation_percent'],
        }
        voting.append(element)

    voting = sorted(voting, key=lambda k: k['min'])

    for el in voting:
        print('{:<16} {} {}'.format(el['name'], el['min'], el['max']))


if __name__ == '__main__':
    main()
