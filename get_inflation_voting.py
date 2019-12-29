#!/usr/bin/env python

import argparse
import logging
import yaml
import statistics

from golos import Steem
from golos.witness import Witness

log = logging.getLogger(__name__)


def get_median_voting(voting, sort_key):
    voting = sorted(voting, key=lambda k: k[sort_key])
    values = [i[sort_key] for i in voting]
    median = statistics.median(values)
    for el in voting:
        print('{name:<16} {worker} {witness} {vesting} {author}'.format(**el))
    log.info('%s_reward_percent median: %s', sort_key, median)

    next_voting = [e for e in voting if e[sort_key] == median]
    return next_voting


def main():

    parser = argparse.ArgumentParser(
        description='get voting props for inflation targets',
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
    formatter = logging.Formatter("%(levelname)s: %(message)s")
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
            'worker': w['props']['worker_reward_percent'],
            'witness': w['props']['witness_reward_percent'],
            'vesting': w['props']['vesting_reward_percent'],
        }
        element['author'] = 10000 - element['worker'] - element['witness'] - element['vesting']
        voting.append(element)

    for key in ['worker', 'witness', 'vesting']:
        voting = get_median_voting(voting, key)


if __name__ == '__main__':
    main()
